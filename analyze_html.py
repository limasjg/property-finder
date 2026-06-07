from scraper import acessar_url
from bs4 import BeautifulSoup
from config import BASE_URL

print("Analisando estrutura HTML do Imovelweb...\n")

response = acessar_url(BASE_URL)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"HTML Length: {len(response.text)} caracteres\n")

# Procura por divs que podem conter imóveis
print("=== Procurando por elementos de imóvel ===\n")

# Tentativa 1: buscar por classe comum
divs = soup.find_all('div', class_=True)
print(f"Total de divs com class: {len(divs)}")

# Procura por padrões de anúncio
padoes_busca = [
    {'name': 'a', 'class_': lambda x: x and 'listing' in ' '.join(x) if isinstance(x, list) else 'listing' in str(x)},
    {'name': 'div', 'class_': lambda x: x and 'anuncio' in ' '.join(x) if isinstance(x, list) else 'anuncio' in str(x)},
    {'name': 'div', 'class_': lambda x: x and 'card' in ' '.join(x) if isinstance(x, list) else 'card' in str(x)},
    {'name': 'article'},
]

for padrao in padoes_busca:
    elementos = soup.find_all(**padrao)
    if elementos:
        print(f"✓ Encontrados {len(elementos)} elementos com padrão: {padrao}")
        if len(elementos) > 0:
            print(f"  Primeiro elemento: {str(elementos[0])[:200]}\n")

# Procura por links
links = soup.find_all('a', href=True)
print(f"\nTotal de links: {len(links)}")

# Procura por preços (padrão: R$ ou dígitos)
pricelike = soup.find_all(string=lambda text: text and 'R$' in str(text))
print(f"Elementos com 'R$': {len(pricelike)}")

# Salva amostra de HTML para análise
with open('html_full.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
    
print("\n✓ HTML completo salvo em 'html_full.html'")
