from scraper import validar_acesso_url, extrair_imoveis, enviar_email
from config import BASE_URL
import json
from datetime import datetime


def main():
    """Função principal"""
    print("=" * 80)
    print("PROPERTY FINDER - Monitoramento de Imóveis")
    print("=" * 80)
    print()
    
    # Etapa 1: Validar acesso
    print("ETAPA 1: Acessar URL")
    print("-" * 80)
    print(f"URL: {BASE_URL}")
    
    if validar_acesso_url():
        print("Status: ✓ Acesso bem-sucedido\n")
    else:
        print("Status: ✗ Falha ao acessar a URL\n")
        return
    
    # Etapa 2-4: Extrair e ordenar imóveis (retornar top 5 mais recentes)
    print("ETAPA 2-4: Extrair, Ordenar por Data e Trazer Top 5 Mais Recentes")
    print("-" * 80)
    
    try:
        imoveis = extrair_imoveis(debug=True, top_n=5)
        print(f"Status: ✓ Encontrados {len(imoveis)} imóveis (top 5 mais recentes)\n")
        
        if len(imoveis) == 0:
            print("Nenhum imóvel encontrado!")
            return
        
        # Exibe os 5 imóveis no console
        print("5 IMOVEIS MAIS RECENTES:")
        print("-" * 80)
        for i, imovel in enumerate(imoveis, 1):
            print(f"\n{i}. {imovel['titulo']}")
            print(f"   Preço: {imovel['preco']}")
            print(f"   Link: {imovel['link']}")
            print(f"   ID: {imovel['id']}")
        
        # Salva resultado em arquivo JSON
        resultado = {
            'data_execucao': datetime.now().isoformat(),
            'total_imoveis': len(imoveis),
            'imoveis': imoveis
        }
        
        nome_arquivo = 'resultado_busca.json'
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        # Salva resultado em arquivo TXT
        nome_arquivo_txt = 'resultado_busca.txt'
        with open(nome_arquivo_txt, 'w', encoding='utf-8') as f:
            f.write("PROPERTY FINDER - 5 Imóveis Mais Recentes\n")
            f.write("=" * 80 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de Imóveis (Top 5): {len(imoveis)}\n")
            f.write(f"URL: {BASE_URL}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, imovel in enumerate(imoveis, 1):
                f.write(f"{i}. {imovel['titulo']}\n")
                f.write(f"   Preço: {imovel['preco']}\n")
                f.write(f"   Link: {imovel['link']}\n")
                f.write(f"   ID: {imovel['id']}\n")
                f.write("-" * 80 + "\n")
        
        print(f"\n✓ Resultados salvos em:")
        print(f"  - {nome_arquivo} (formato JSON)")
        print(f"  - {nome_arquivo_txt} (formato texto)")
        
        # Etapa 5: Enviar por email
        print("\nETAPA 5: Enviar por Email")
        print("-" * 80)
        
        if enviar_email(imoveis, debug=True):
            print("Status: ✓ Email enviado com sucesso!\n")
        else:
            print("Status: ✗ Falha ao enviar email\n")
            print("Dica: Configure a App Password do Gmail em .env")
        
    except Exception as e:
        print(f"Status: ✗ Erro na extração: {e}")


if __name__ == "__main__":
    main()
