from playwright.sync_api import sync_playwright
from config import BASE_URL
import time

try:
    print(f"URL: {BASE_URL}\n")
    print("Acessando com Playwright (timeout 30s, domcontentloaded)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        
        time.sleep(3)
        
        html = page.content()
        
        print(f"Status: {response.status if response else 'None'}")
        print(f"HTML length: {len(html)}")
        print(f"First 500 chars:\n{html[:500]}")
        
        browser.close()
        
except Exception as e:
    print(f"Erro: {type(e).__name__}")
    print(f"Detalhes: {e}")

