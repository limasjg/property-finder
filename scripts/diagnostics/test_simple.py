import requests
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from property_finder.config import HEADERS, REQUEST_TIMEOUT

# Testa URL simples para validar que cloudscraper/requests funciona
urls_teste = [
    "https://www.imovelweb.com.br/",  # Home page
    "https://www.google.com",  # Teste simples
]

for url in urls_teste:
    print(f"\nTestando: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        print(f"✓ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Erro: {e}")
