import cloudscraper
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from property_finder.config import BASE_URL, REQUEST_TIMEOUT, HEADERS

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

