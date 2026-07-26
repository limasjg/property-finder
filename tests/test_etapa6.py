import pytest
import os
import json

from property_finder.scraper import carregar_ids_vistos, salvar_ids_vistos, filtrar_novos_imoveis, _gerar_fingerprint


IMOVEIS_MOCK = [
    {'id': '1001', 'titulo': 'Casa no Bacacheri', 'preco': 'R$ 450.000', 'link': 'https://www.imovelweb.com.br/propriedades/1001', 'imagem': 'N/A'},
    {'id': '1002', 'titulo': 'Sobrado no Batel',  'preco': 'R$ 590.000', 'link': 'https://www.imovelweb.com.br/propriedades/1002', 'imagem': 'N/A'},
    {'id': '1003', 'titulo': 'Apto no Bigorrilho', 'preco': 'R$ 380.000', 'link': 'https://www.imovelweb.com.br/propriedades/1003', 'imagem': 'N/A'},
]


class TestEtapa6:

    # --- carregar_ids_vistos ---

    def test_carregar_ids_arquivo_inexistente(self, tmp_path):
        """Retorna conjunto vazio se arquivo não existe"""
        ids, fps = carregar_ids_vistos(str(tmp_path / 'nao_existe.json'))
        assert ids == set() and fps == set()

    def test_carregar_ids_arquivo_corrompido(self, tmp_path):
        """Retorna conjunto vazio se arquivo está corrompido"""
        arquivo = tmp_path / 'corrompido.json'
        arquivo.write_text("INVALIDO")
        ids, fps = carregar_ids_vistos(str(arquivo))
        assert ids == set() and fps == set()

    # --- salvar_ids_vistos ---

    def test_salvar_cria_arquivo(self, tmp_path):
        """Deve criar o arquivo JSON ao salvar"""
        arquivo = str(tmp_path / 'ids.json')
        salvar_ids_vistos({'111', '222'}, arquivo)
        assert os.path.exists(arquivo)

    def test_salvar_conteudo_correto(self, tmp_path):
        """Arquivo salvo deve conter 'ids', 'fingerprints' e 'ultima_execucao'"""
        arquivo = str(tmp_path / 'ids.json')
        salvar_ids_vistos({'aaa', 'bbb'}, arquivo)
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        assert 'ids' in dados
        assert 'fingerprints' in dados
        assert 'ultima_execucao' in dados
        assert set(dados['ids']) == {'aaa', 'bbb'}

    def test_round_trip_salvar_e_carregar(self, tmp_path):
        """IDs salvos devem ser retornados intactos ao carregar"""
        arquivo = str(tmp_path / 'ids.json')
        ids_originais = {'100', '200', '300'}
        salvar_ids_vistos(ids_originais, arquivo)
        ids_carregados, _ = carregar_ids_vistos(arquivo)
        assert ids_carregados == ids_originais

    # --- filtrar_novos_imoveis ---

    def test_filtrar_todos_novos_quando_vistos_vazio(self):
        """Retorna todos os imóveis quando nenhum foi visto antes"""
        novos = filtrar_novos_imoveis(IMOVEIS_MOCK, set())
        assert len(novos) == len(IMOVEIS_MOCK)

    def test_filtrar_nenhum_novo_quando_todos_vistos(self):
        """Retorna lista vazia quando todos os IDs já foram vistos"""
        ids_vistos = {'1001', '1002', '1003'}
        novos = filtrar_novos_imoveis(IMOVEIS_MOCK, ids_vistos)
        assert novos == []

    def test_filtrar_retorna_apenas_nao_vistos(self):
        """Retorna somente os imóveis com ID ainda não visto"""
        ids_vistos = {'1001', '1002'}
        novos = filtrar_novos_imoveis(IMOVEIS_MOCK, ids_vistos)
        assert len(novos) == 1
        assert novos[0]['id'] == '1003'

    def test_filtrar_respeita_limite_max_novos(self):
        """Não deve retornar mais do que max_novos imóveis"""
        imoveis = [
            {'id': str(i), 'titulo': f'Casa {i}', 'preco': 'R$ 100.000',
             'link': f'https://x.com/{i}', 'imagem': 'N/A'}
            for i in range(1, 20)
        ]
        novos = filtrar_novos_imoveis(imoveis, set(), max_novos=8)
        assert len(novos) == 8

    def test_filtrar_ignora_imoveis_sem_id(self):
        """Imóveis com id='N/A' devem ser ignorados"""
        imoveis = [
            {'id': 'N/A', 'titulo': 'Sem ID', 'preco': 'R$ 100', 'link': 'http://x', 'imagem': 'N/A'},
            {'id': '999', 'titulo': 'Com ID', 'preco': 'R$ 200', 'link': 'http://y', 'imagem': 'N/A'},
        ]
        novos = filtrar_novos_imoveis(imoveis, set())
        assert len(novos) == 1
        assert novos[0]['id'] == '999'

    def test_filtrar_lista_vazia_retorna_vazia(self):
        """Lista vazia de entrada deve retornar lista vazia"""
        novos = filtrar_novos_imoveis([], set())
        assert novos == []

    def test_filtrar_nao_retorna_duplicatas(self):
        """Mesmo que haja IDs repetidos na entrada, não retorna duplicatas"""
        imoveis_com_dup = IMOVEIS_MOCK + [IMOVEIS_MOCK[0]]  # 1001 repetido
        novos = filtrar_novos_imoveis(imoveis_com_dup, set())
        ids = [im['id'] for im in novos]
        assert len(ids) == len(set(ids)), "Há IDs duplicados no resultado"

    def test_filtrar_preserva_dados_do_imovel(self):
        """Os dados dos imóveis novos não devem ser alterados"""
        novos = filtrar_novos_imoveis(IMOVEIS_MOCK, set())
        assert novos[0]['titulo'] == IMOVEIS_MOCK[0]['titulo']
        assert novos[0]['preco'] == IMOVEIS_MOCK[0]['preco']
        assert novos[0]['link'] == IMOVEIS_MOCK[0]['link']

    def test_filtrar_dedup_por_fingerprint_mesmo_conteudo(self):
        """Dois imóveis com mesmo título e preço mas IDs diferentes são tratados como um"""
        imoveis = [
            {'id': '1111', 'titulo': 'Casa no Bacacheri', 'preco': 'R$ 450.000',
             'link': 'http://x/1111', 'imagem': 'N/A'},
            {'id': '2222', 'titulo': 'Casa no Bacacheri', 'preco': 'R$ 450.000',
             'link': 'http://x/2222', 'imagem': 'N/A'},
        ]
        novos = filtrar_novos_imoveis(imoveis, set())
        assert len(novos) == 1

    def test_filtrar_fingerprint_cross_run(self):
        """Imóvel que mudou data-id mas manteve título/preço é reconhecido como visto"""
        fp = _gerar_fingerprint('Casa no Bacacheri', 'R$ 450.000')
        imovel = {'id': '9999', 'titulo': 'Casa no Bacacheri', 'preco': 'R$ 450.000',
                  'link': 'http://x/9999', 'imagem': 'N/A'}
        novos = filtrar_novos_imoveis([imovel], set(), fingerprints_vistos={fp})
        assert novos == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
