from bs4 import BeautifulSoup

with open('html_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Encontra primeiro card
cards = soup.find_all('div', attrs={'data-posting-type': 'PROPERTY'})
print(f"Total de cards: {len(cards)}\n")

if cards:
    card = cards[0]
    print("=" * 100)
    print("PRIMEIRO CARD (COMPLETO):")
    print("=" * 100)
    print(card.prettify()[:2000])
    
    print("\n" + "=" * 100)
    print("ANÁLISE DO CARD:")
    print("=" * 100)
    
    # Análise de seletores
    print("\nTodos os links no card:")
    for i, link in enumerate(card.find_all('a')[:3], 1):
        print(f"  {i}. href={link.get('href')} | texto={link.get_text(strip=True)[:50]}")
    
    print("\nTodos os textos contendo 'R$':")
    for i, texto in enumerate(card.strings):
        if 'R$' in texto:
            print(f"  {texto.strip()}")
    
    print("\nTodos os elementos com class:")
    for elem in card.find_all(['div', 'p', 'span', 'h1', 'h2', 'h3']):
        if elem.get('class'):
            print(f"  {elem.name} class={' '.join(elem.get('class'))} - {elem.get_text(strip=True)[:60]}")
