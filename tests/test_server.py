import json

import server


IMOVEIS = [
    {
        'id': str(numero),
        'titulo': f'Imóvel {numero}',
        'preco': f'R$ {numero}',
        'link': f'https://example.com/{numero}',
        'imagem': 'N/A',
    }
    for numero in range(1, 11)
]


def test_historico_le_cache_sem_acessar_rede(monkeypatch, tmp_path):
    arquivo = tmp_path / 'historico_busca.json'
    arquivo.write_text(json.dumps({
        'data_execucao': '2026-08-08T10:00:00',
        'imoveis': IMOVEIS,
    }), encoding='utf-8')
    monkeypatch.setattr(server, 'ARQUIVO_HISTORICO', arquivo)
    monkeypatch.setattr(server, 'OUTPUT_DIR', tmp_path)

    def nao_deveria_acessar_rede(**kwargs):
        raise AssertionError('o histórico não deve acessar a rede')

    monkeypatch.setattr(server, 'extrair_imoveis', nao_deveria_acessar_rede)

    with server.app.test_client() as client:
        response = client.get('/api/historico')

    dados = response.get_json()
    assert response.status_code == 200
    assert dados['historico'] == IMOVEIS[:8]
    assert dados['total'] == 8
    assert dados['data_execucao'] == '2026-08-08T10:00:00'
    assert dados['version'] == server.APP_VERSION
    assert response.headers['X-Property-Finder-Version'] == server.APP_VERSION
    assert 'no-store' in response.headers['Cache-Control']


def test_historico_usa_resultado_legado(monkeypatch, tmp_path):
    (tmp_path / 'resultado_busca.json').write_text(json.dumps({
        'data_execucao': '2026-08-07T09:00:00',
        'imoveis': IMOVEIS[:2],
    }), encoding='utf-8')
    monkeypatch.setattr(server, 'ARQUIVO_HISTORICO', tmp_path / 'inexistente.json')
    monkeypatch.setattr(server, 'OUTPUT_DIR', tmp_path)

    with server.app.test_client() as client:
        response = client.get('/api/historico')

    assert response.status_code == 200
    assert response.get_json()['historico'] == IMOVEIS[:2]


def test_salvar_historico_limita_a_oito(monkeypatch, tmp_path):
    arquivo = tmp_path / 'historico_busca.json'
    monkeypatch.setattr(server, 'ARQUIVO_HISTORICO', arquivo)

    server.salvar_historico(IMOVEIS)

    dados = json.loads(arquivo.read_text(encoding='utf-8'))
    assert dados['total'] == 8
    assert dados['imoveis'] == IMOVEIS[:8]


def test_erro_de_rede_bloqueada_tem_orientacao_util():
    mensagem = server.mensagem_erro_scraping(
        RuntimeError('Page.goto: net::ERR_NETWORK_ACCESS_DENIED')
    )

    assert 'bloqueou o acesso externo' in mensagem
    assert 'firewall' in mensagem
