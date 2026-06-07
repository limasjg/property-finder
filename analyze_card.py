from bs4 import BeautifulSoup

with open('html_sample.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Procura por diversos padrões
print("Procurando por imóveis...\n")

# Padrão 1: div com data-id e data-posting-type
cards1 = soup.find_all('div', attrs={'data-posting-type': 'PROPERTY'})
print(f"Cards com data-posting-type='PROPERTY': {len(cards1)}")

# Padrão 2: div com class contendo 'posting'
cards2 = soup.find_all('div', class_=lambda x: x and 'posting' in ' '.join(x) if isinstance(x, list) else 'posting' in str(x))
print(f"Divs com 'posting' na class: {len(cards2)}")

# Padrão 3: links com href
links = soup.find_all('a', href=lambda x: x and '/imovei/' in x)
print(f"Links com '/imovei/': {len(links)}")

if cards1:
    print("\n=== PRIMEIRO CARD (com data-posting-type) ===")
    card = cards1[0]
    print(str(card)[:1000])
    
    # Tenta extrair texto
    print("\nTexto completo do card:")
    print(card.get_text()[:500])

if links:
    print("\n=== PRIMEIRO LINK ===")
    link = links[0]
    print(f"href: {link.get('href')}")
    print(f"Texto: {link.get_text()}")
    
    # Procura por preço próximo ao link
    parent = link.parent
    for _ in range(3):
        if parent:
            texto = parent.get_text()
            if 'R$' in texto:
                print(f"Preço no parent: {texto[:200]}")
                break
            parent = parent.parent
