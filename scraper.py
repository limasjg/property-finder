from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from config import BASE_URL, REQUEST_TIMEOUT, HEADERS
import time


def acessar_url(url=None):
    """
    Acessa uma URL e retorna a resposta.
    Usa Playwright para contornar proteções anti-bot.
    
    Args:
        url (str, opcional): URL a ser acessada. Usa BASE_URL se não fornecida.
    
    Returns:
        Response: Objeto com status_code e text.
    
    Raises:
        Exception: Se a requisição falhar.
    """
    if url is None:
        url = BASE_URL
    
    with sync_playwright() as p:
        # Usa browser com modo headless
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Configura User-Agent e headers para parecer real
        page.set_extra_http_headers(HEADERS)
        
        try:
            # Navega para a URL com timeout maior
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # IMPORTANTE: Aguarda desafio do Cloudflare ser resolvido
            # Verifica se está na página de desafio
            print(f"[DEBUG] Aguardando resolução do Cloudflare...")
            for i in range(30):  # Tenta por até 30 segundos
                html = page.content()
                
                # Verifica se página carregou (tamanho > 5000 bytes)
                if "Just a moment" not in html and len(html) > 5000:
                    print(f"[DEBUG] OK - Página carregada em {i} segundos!")
                    break
                    
                # Tenta clicar em qualquer elemento interativo se necessário
                if i == 5 and "Just a moment" in html:
                    try:
                        # Procura por botão de verificação
                        page.click('button', force=True)
                    except:
                        pass
                
                if i % 5 == 0:
                    print(f"[DEBUG] Aguardando... {i}s - HTML length: {len(html)}")
                    
                time.sleep(1)
            
            # Aguarda renderização de conteúdo dinâmico
            time.sleep(2)
            
            # Obtém o HTML
            html = page.content()
            
            # Cria objeto compatível
            class Response:
                def __init__(self, status_code, text):
                    self.status_code = status_code
                    self.text = text
                    self.content = text.encode('utf-8')
                    self.headers = {'Content-Type': 'text/html; charset=utf-8'}
            
            status = response.status if response else 200
            return Response(status, html)
        
        finally:
            browser.close()


def validar_acesso_url(url=None):
    """
    Valida se é possível acessar a URL e obter conteúdo real.
    
    Args:
        url (str, opcional): URL a ser validada.
    
    Returns:
        bool: True se conseguir acessar, False caso contrário.
    """
    try:
        response = acessar_url(url)
        # Valida se conseguiu carregar conteúdo REAL (não desafio Cloudflare)
        sucesso = (
            response.status_code in [200, 403] and 
            len(response.text) > 1000 and
            "Just a moment" not in response.text  # Não está mais no desafio
        )
        return sucesso
    except Exception as e:
        return False


def extrair_imoveis(url=None, debug=False, top_n=None):
    """
    Extrai lista de imóveis da página.
    
    Args:
        url (str, opcional): URL a ser processada. Usa BASE_URL se não fornecida.
        debug (bool): Se True, exibe informações de debug.
        top_n (int, opcional): Se fornecido, retorna apenas os N primeiros imóveis (mais recentes).
                               A URL retorna em ordem decrescente de data.
    
    Returns:
        list: Lista de dicionários com dados dos imóveis.
              Cada dicionário tem: {'titulo', 'preco', 'link', 'data_id'}
    
    Raises:
        Exception: Se a extração falhar.
    """
    if url is None:
        url = BASE_URL
    
    response = acessar_url(url)
    
    if debug:
        print(f"[EXTRACT DEBUG] HTML Length: {len(response.text)}")
        print(f"[EXTRACT DEBUG] Contém 'Just a moment': {'Just a moment' in response.text}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    imoveis = []
    
    # Padrão 1: Procura por cards com data-posting-type="PROPERTY"
    cards = soup.find_all('div', attrs={'data-posting-type': 'PROPERTY'})
    
    if debug:
        print(f"[EXTRACT DEBUG] Cards encontrados (padrão 1): {len(cards)}")
    
    # Se não encontrou, tenta padrão 2
    if not cards:
        # Padrão 2: Procura por divs que contenham classe 'postingCard'
        cards = soup.find_all('div', class_=lambda x: x and 'postingCard' in ' '.join(x) if isinstance(x, list) else 'postingCard' in str(x))
        if debug:
            print(f"[EXTRACT DEBUG] Cards encontrados (padrão 2): {len(cards)}")
    
    # Se ainda não encontrou, tenta padrão 3
    if not cards:
        # Padrão 3: Procura por divs com classe 'listing'
        cards = soup.find_all('div', class_=lambda x: x and 'listing' in ' '.join(x) if isinstance(x, list) else 'listing' in str(x))
        if debug:
            print(f"[EXTRACT DEBUG] Cards encontrados (padrão 3): {len(cards)}")
    
    for idx, card in enumerate(cards):
        try:
            # Extrai ID do imóvel
            imovel_id = card.get('data-id', 'N/A')
            
            # Extrai link - procura por primeiro link que contém imóvel
            link = 'N/A'
            link_elem = card.find('a', href=lambda x: x and '/propriedades/' in x if x else False)
            if link_elem:
                link = link_elem.get('href', 'N/A')
                # Formata URL para ser completa
                if link and not link.startswith('http'):
                    link = 'https://www.imovelweb.com.br' + link
            
            # Extrai título principal
            # Procura por h2 com classe 'posting-description'
            titulo = 'N/A'
            titulo_elem = card.find('h2', class_=lambda x: x and 'posting-description' in ' '.join(x) if isinstance(x, list) else 'posting-description' in str(x))
            if titulo_elem:
                titulo = titulo_elem.get_text(strip=True)
            
            # Se não encontrou, tenta pelo link
            if titulo == 'N/A' and link_elem:
                titulo_text = link_elem.get_text(strip=True)
                if titulo_text:
                    titulo = titulo_text
            
            # Procura por preço
            preco = 'N/A'
            # Procura por h2 ou span com preço
            price_elem = card.find('h2', class_=lambda x: x and 'price' in ' '.join(x) if isinstance(x, list) else 'price' in str(x))
            if price_elem:
                preco = price_elem.get_text(strip=True)
            else:
                # Alternativa: procura por texto contendo R$
                for texto in card.strings:
                    texto_str = texto.strip()
                    if 'R$' in texto_str and len(texto_str) < 30:  # Filtro para não pegar descrição longa
                        preco = texto_str
                        break
            
            # Somente adiciona se temos dados válidos
            if titulo != 'N/A' or preco != 'N/A' or link != 'N/A':
                imovel = {
                    'id': imovel_id,
                    'titulo': titulo,
                    'preco': preco,
                    'link': link
                }
                
                imoveis.append(imovel)
                
                if debug and idx < 3:
                    print(f"[EXTRACT DEBUG] Imóvel {idx+1}:")
                    print(f"  - Título: {titulo[:60]}")
                    print(f"  - Preço: {preco}")
                    print(f"  - Link: {link[:70]}")
        
        except Exception as e:
            if debug:
                print(f"[EXTRACT DEBUG] Erro ao processar card {idx}: {e}")
            continue
    
    # Retorna apenas top_n se especificado
    if top_n:
        imoveis = imoveis[:top_n]
        if debug:
            print(f"[EXTRACT DEBUG] Retornando apenas {top_n} imóveis mais recentes")
    
    return imoveis


def enviar_email(imoveis, debug=False):
    """
    Envia os imóveis extraídos por email em formato HTML.
    
    Args:
        imoveis (list): Lista de dicionários com dados dos imóveis.
        debug (bool): Se True, exibe informações de debug.
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário.
    
    Raises:
        Exception: Se houver erro no envio.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from config import EMAIL_SENDER, EMAIL_RECIPIENT, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
    from datetime import datetime
    
    if not EMAIL_PASSWORD:
        print("[EMAIL ERROR] EMAIL_PASSWORD não configurada!")
        print("[EMAIL INFO] Configure a variável de ambiente ou arquivo .env")
        return False
    
    try:
        # Cria mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Property Finder - {len(imoveis)} Imóveis Mais Recentes ({datetime.now().strftime('%d/%m/%Y')})"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        
        # Cria HTML com os imóveis
        html_content = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                    .imovel {{ 
                        background-color: #f8f9fa; 
                        margin: 20px 0; 
                        padding: 15px; 
                        border-left: 4px solid #3498db;
                        border-radius: 4px;
                    }}
                    .numero {{ color: #3498db; font-weight: bold; font-size: 16px; }}
                    .titulo {{ font-weight: bold; color: #2c3e50; margin: 10px 0 5px 0; }}
                    .preco {{ color: #27ae60; font-size: 18px; font-weight: bold; margin: 5px 0; }}
                    .link {{ color: #3498db; text-decoration: none; word-break: break-all; }}
                    .link:hover {{ text-decoration: underline; }}
                    .id {{ color: #95a5a6; font-size: 12px; margin-top: 5px; }}
                    .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #95a5a6; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Property Finder - {len(imoveis)} Imóveis Mais Recentes</h1>
                    <p>Executado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
        """
        
        # Adiciona cada imóvel
        for idx, imovel in enumerate(imoveis, 1):
            html_content += f"""
                    <div class="imovel">
                        <div class="numero">#{idx}</div>
                        <div class="titulo">{imovel['titulo'][:200]}...</div>
                        <div class="preco">{imovel['preco']}</div>
                        <div><a href="{imovel['link']}" class="link" target="_blank">Ver anúncio completo →</a></div>
                        <div class="id">ID: {imovel['id']}</div>
                    </div>
            """
        
        html_content += """
                    <div class="footer">
                        <p>Monitoramento automático de imóveis do Imovelweb</p>
                        <p>Property Finder - 2026</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Cria parte de texto puro (fallback)
        text_content = f"Property Finder - {len(imoveis)} Imóveis Mais Recentes\n"
        text_content += "=" * 80 + "\n"
        text_content += f"Executado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n\n"
        
        for idx, imovel in enumerate(imoveis, 1):
            text_content += f"{idx}. {imovel['titulo'][:200]}...\n"
            text_content += f"   Preço: {imovel['preco']}\n"
            text_content += f"   Link: {imovel['link']}\n"
            text_content += f"   ID: {imovel['id']}\n\n"
        
        # Adiciona partes à mensagem
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # Conecta ao servidor SMTP e envia
        if debug:
            print(f"[EMAIL DEBUG] Conectando a {SMTP_SERVER}:{SMTP_PORT}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            
            if debug:
                print(f"[EMAIL DEBUG] Autenticando como {EMAIL_SENDER}...")
            
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            
            if debug:
                print(f"[EMAIL DEBUG] Enviando para {EMAIL_RECIPIENT}...")
            
            server.send_message(msg)
        
        if debug:
            print(f"[EMAIL DEBUG] Email enviado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"[EMAIL ERROR] Erro ao enviar email: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False
