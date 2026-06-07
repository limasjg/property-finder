import cloudscraper
from config import BASE_URL, REQUEST_TIMEOUT, HEADERS

try:
    print(f"URL: {BASE_URL}\n")
    
    scraper = cloudscraper.create_scraper()
    
    print("Fazendo requisição com cloudscraper...")
    response = scraper.get(
        BASE_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content Length: {len(response.content)}")
    print(f"HTML preview (primeiros 500 chars):")
    print(response.text[:500])
    
except Exception as e:
    print(f"Erro: {type(e).__name__}")
    print(f"Detalhes: {e}")
    import traceback
    traceback.print_exc()

