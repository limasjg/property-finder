#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Property Finder Web Server
Servidor local para testar o scraper com interface visual moderna.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from property_finder.scraper import (
    extrair_imoveis,
    carregar_ids_vistos,
    salvar_ids_vistos,
    filtrar_novos_imoveis,
    _gerar_fingerprint,
)
from property_finder.config import BASE_URL, ARQUIVO_IDS_VISTOS, DATA_DIR, OUTPUT_DIR

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False
APP_VERSION = '2026.08.08-cache-v2'
ARQUIVO_HISTORICO = OUTPUT_DIR / 'historico_busca.json'


def ensure_dirs():
    """Cria diretórios necessários."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.after_request
def desabilitar_cache_api(response):
    """Evita que o navegador reutilize respostas de uma versão antiga da API."""
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Property-Finder-Version'] = APP_VERSION
    return response


def salvar_historico(imoveis):
    """Persiste os oito imóveis mais recentes da última busca bem-sucedida."""
    historico = {
        'data_execucao': datetime.now().isoformat(),
        'total': min(len(imoveis), 8),
        'imoveis': imoveis[:8],
    }
    arquivo_temporario = ARQUIVO_HISTORICO.with_suffix('.tmp')
    with open(arquivo_temporario, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)
    arquivo_temporario.replace(ARQUIVO_HISTORICO)


def carregar_historico():
    """Carrega o cache atual ou o resultado legado, se ainda não houver cache."""
    arquivos = (
        (ARQUIVO_HISTORICO, 'imoveis'),
        (OUTPUT_DIR / 'resultado_busca.json', 'imoveis'),
    )
    for arquivo, campo in arquivos:
        if not arquivo.exists():
            continue
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            imoveis = dados.get(campo, [])
            if isinstance(imoveis, list):
                return imoveis[:8], dados.get('data_execucao')
        except (OSError, json.JSONDecodeError, AttributeError):
            continue
    return [], None


def mensagem_erro_scraping(erro):
    """Converte erros técnicos de rede em uma orientação útil para o usuário."""
    detalhe = str(erro)
    if 'ERR_NETWORK_ACCESS_DENIED' in detalhe or 'WinError 10013' in detalhe:
        return (
            'O ambiente onde o servidor foi iniciado bloqueou o acesso externo. '
            'Execute o server.py em um PowerShell/terminal com acesso à internet '
            'e libere o Python/Chromium no firewall, se solicitado.'
        )
    return f'Erro ao acessar o Imovelweb: {detalhe}'


@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Retorna o status do scraper (último histórico)."""
    ensure_dirs()

    try:
        ids_vistos, fps_vistos = carregar_ids_vistos(ARQUIVO_IDS_VISTOS)

        # Tenta carregar resultado da última execução
        resultado_json = OUTPUT_DIR / 'resultado_busca.json'
        ultimo_resultado = None
        if resultado_json.exists():
            with open(resultado_json, 'r', encoding='utf-8') as f:
                ultimo_resultado = json.load(f)

        return jsonify({
            'success': True,
            'version': APP_VERSION,
            'status': {
                'url': BASE_URL,
                'ids_vistos': len(ids_vistos),
                'fingerprints_vistos': len(fps_vistos),
                'ultimo_resultado': ultimo_resultado,
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/buscar', methods=['POST'])
def api_buscar():
    """Executa o scraper e retorna os imóveis novos encontrados."""
    ensure_dirs()

    try:
        # A própria extração valida o acesso. Fazer uma navegação separada aqui
        # duplicava o tempo da busca e descartava o motivo real de erros de rede.
        imoveis = extrair_imoveis(debug=False)
        if not imoveis:
            return jsonify({
                'success': True,
                'novos': [],
                'mensagem': 'Nenhum imóvel encontrado na página.'
            })

        # O histórico representa a última página consultada, não apenas os
        # anúncios que passaram pelo filtro de novidades.
        salvar_historico(imoveis)

        # Carrega histórico
        ids_vistos, fingerprints_vistos = carregar_ids_vistos(ARQUIVO_IDS_VISTOS)

        # Filtra novos
        novos = filtrar_novos_imoveis(imoveis, ids_vistos, fingerprints_vistos, max_novos=8)

        # Salva histórico
        ids_atuais = {im['id'] for im in imoveis if im['id'] != 'N/A'}
        fps_atuais = {_gerar_fingerprint(im.get('titulo', 'N/A'), im.get('preco', 'N/A'))
                      for im in imoveis}
        salvar_ids_vistos(ids_vistos | ids_atuais, ARQUIVO_IDS_VISTOS,
                          fingerprints=fingerprints_vistos | fps_atuais)

        # Salva resultado
        resultado = {
            'data_execucao': datetime.now().isoformat(),
            'total_novos': len(novos),
            'imoveis': novos,
        }
        resultado_path = OUTPUT_DIR / 'resultado_busca.json'
        with open(resultado_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'novos': novos,
            'total': len(novos),
            'mensagem': f'{len(novos)} imóvel(is) novo(s) encontrado(s)!'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': mensagem_erro_scraping(e)
        }), 500


@app.route('/api/historico')
def api_historico():
    """Retorna os últimos 8 imóveis salvos, sem depender de acesso externo."""
    ensure_dirs()
    try:
        imoveis, data_execucao = carregar_historico()
        if not imoveis:
            return jsonify({
                'success': True,
                'version': APP_VERSION,
                'historico': [],
                'total': 0,
                'mensagem': 'Nenhum histórico salvo. Faça uma busca primeiro.'
            })

        return jsonify({
            'success': True,
            'version': APP_VERSION,
            'historico': imoveis,
            'total': len(imoveis),
            'data_execucao': data_execucao,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar histórico: {str(e)}'
        }), 500


if __name__ == '__main__':
    try:
        server_port = int(os.getenv('PROPERTY_FINDER_PORT', '5001'))
    except ValueError:
        server_port = 5001

    print("=" * 80)
    print("PROPERTY FINDER - Web Server")
    print("=" * 80)
    print()
    print(f"Acessar em: http://localhost:{server_port}")
    print(f"Versão: {APP_VERSION}")
    print(f"Arquivo: {Path(__file__).resolve()}")
    print()
    # O reloader pode reiniciar o processo durante o scraping e interromper o
    # fetch do navegador. O debug continua opcional, mas sempre sem reloader.
    debug_enabled = os.getenv('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'}
    app.run(debug=debug_enabled, use_reloader=False, port=server_port)
