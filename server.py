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
    validar_acesso_url,
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


def ensure_dirs():
    """Cria diretórios necessários."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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
        # Valida acesso à URL
        if not validar_acesso_url():
            return jsonify({
                'success': False,
                'error': 'Falha ao acessar a URL. Verifique sua conexão.'
            }), 500

        # Extrai imóveis
        imoveis = extrair_imoveis(debug=False)
        if not imoveis:
            return jsonify({
                'success': True,
                'novos': [],
                'mensagem': 'Nenhum imóvel encontrado na página.'
            })

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
            'error': f'Erro ao buscar imóveis: {str(e)}'
        }), 500


@app.route('/api/historico')
def api_historico():
    """Retorna o histórico de buscas."""
    try:
        resultado_path = OUTPUT_DIR / 'resultado_busca.json'
        if not resultado_path.exists():
            return jsonify({'success': True, 'historico': []})

        with open(resultado_path, 'r', encoding='utf-8') as f:
            resultado = json.load(f)

        return jsonify({
            'success': True,
            'historico': resultado.get('imoveis', []),
            'data_execucao': resultado.get('data_execucao', None),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("PROPERTY FINDER - Web Server")
    print("=" * 80)
    print()
    print("Acessar em: http://localhost:5000")
    print()
    app.run(debug=True, port=5000)
