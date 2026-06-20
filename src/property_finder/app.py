import json
from datetime import datetime
from pathlib import Path

from .scraper import (
    validar_acesso_url,
    extrair_imoveis,
    enviar_email,
    carregar_ids_vistos,
    salvar_ids_vistos,
    filtrar_novos_imoveis,
)
from .config import BASE_URL, ARQUIVO_IDS_VISTOS, ARQUIVO_RESULTADO_JSON, DATA_DIR, OUTPUT_DIR


def main():
    """Função principal."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("PROPERTY FINDER - Monitoramento de Imóveis")
    print("=" * 80)
    print()

    print("ETAPA 1: Acessar URL")
    print("-" * 80)
    print(f"URL: {BASE_URL}")

    if validar_acesso_url():
        print("Status: ✓ Acesso bem-sucedido\n")
    else:
        print("Status: ✗ Falha ao acessar a URL\n")
        return

    print("ETAPA 2-4: Extrair Imóveis da Primeira Página")
    print("-" * 80)

    try:
        imoveis = extrair_imoveis(debug=True)
        print(f"Status: ✓ Encontrados {len(imoveis)} imóveis na página\n")

        ids_vistos = carregar_ids_vistos(ARQUIVO_IDS_VISTOS)
        print(f"IDs já vistos anteriormente: {len(ids_vistos)}")

        if not imoveis:
            print("Nenhum imóvel encontrado na página!")
            return

        print("\nETAPA 6: Comparar com Anúncios Anteriores")
        print("-" * 80)

        novos = filtrar_novos_imoveis(imoveis, ids_vistos, max_novos=8)
        print(f"Novos anúncios encontrados: {len(novos)}")

        ids_atuais = {im['id'] for im in imoveis if im['id'] != 'N/A'}
        salvar_ids_vistos(ids_vistos | ids_atuais, ARQUIVO_IDS_VISTOS)
        print(f"IDs salvos para próxima execução: {len(ids_vistos | ids_atuais)}")

        if not novos:
            print("\nStatus: ✓ Nenhum anúncio novo encontrado - email não enviado\n")
            return

        print(f"\n{len(novos)} ANÚNCIO(S) NOVO(S):")
        print("-" * 80)
        for i, imovel in enumerate(novos, 1):
            print(f"\n{i}. {imovel['titulo']}")
            print(f"   Preço: {imovel['preco']}")
            print(f"   Link: {imovel['link']}")
            print(f"   ID: {imovel['id']}")

        resultado = {
            'data_execucao': datetime.now().isoformat(),
            'total_novos': len(novos),
            'imoveis': novos,
        }
        resultado_path = Path(ARQUIVO_RESULTADO_JSON)
        with open(resultado_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Resultado salvo em {resultado_path}")

        print("\nETAPA 5: Enviar por Email")
        print("-" * 80)

        if enviar_email(novos, debug=True):
            print("Status: ✓ Email enviado com sucesso!\n")
        else:
            print("Status: ✗ Falha ao enviar email\n")
            print("Dica: Configure a App Password do Gmail em .env")

    except Exception as e:
        print(f"Status: ✗ Erro: {e}")
