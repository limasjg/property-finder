from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .config import BASE_URL, REQUEST_TIMEOUT, HEADERS
from html import escape
import time
import os
import json


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
            print(f"[DEBUG] Aguardando resolução do Cloudflare...")
            for i in range(30):  # Tenta por até 30 segundos
                html = page.content()

                if "Just a moment" not in html and len(html) > 5000:
                    print(f"[DEBUG] OK - Cloudflare resolvido em {i} segundos!")
                    break

                if i == 5 and "Just a moment" in html:
                    try:
                        page.click('button', force=True)
                    except:
                        pass

                if i % 5 == 0:
                    print(f"[DEBUG] Aguardando... {i}s - HTML length: {len(html)}")

                time.sleep(1)

            # Aguarda os cards de imóveis aparecerem no DOM (conteúdo dinâmico)
            SELECTOR_CARDS = '[data-posting-type="PROPERTY"]'
            try:
                page.wait_for_selector(SELECTOR_CARDS, timeout=20000)
                print(f"[DEBUG] Cards de imóveis detectados no DOM!")
            except Exception:
                # Site pode estar sem resultados ou com estrutura diferente;
                # continua com o HTML disponível
                print(f"[DEBUG] Timeout aguardando cards — continuando com HTML atual (len={len(page.content())})")
            
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


def extrair_imagem_card(card):
    """
    Extrai a URL da imagem principal de um card de imóvel.
    """
    for img in card.find_all('img'):
        imagem = (
            img.get('src') or
            img.get('data-src') or
            img.get('data-flickity-lazyload') or
            img.get('data-original')
        )

        if not imagem:
            continue

        if imagem.startswith('//'):
            imagem = 'https:' + imagem
        elif imagem.startswith('/'):
            imagem = 'https://www.imovelweb.com.br' + imagem

        # Fotos dos anúncios ficam em /avisos/; logos de imobiliárias ficam em outro caminho.
        if '/avisos/' in imagem:
            return imagem

    return 'N/A'


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
              Cada dicionário tem: {'titulo', 'preco', 'link', 'id', 'imagem'}
    
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
    ids_extraidos = set()  # controle de duplicatas por ID
    
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

            imagem = extrair_imagem_card(card)
            
            # Somente adiciona se temos dados válidos e ID ainda não visto
            if titulo != 'N/A' or preco != 'N/A' or link != 'N/A':
                if imovel_id in ids_extraidos:
                    if debug:
                        print(f"[EXTRACT DEBUG] Duplicata ignorada: ID {imovel_id}")
                    continue
                ids_extraidos.add(imovel_id)
                imovel = {
                    'id': imovel_id,
                    'titulo': titulo,
                    'preco': preco,
                    'link': link,
                    'imagem': imagem
                }
                
                imoveis.append(imovel)
                
                if debug and idx < 3:
                    print(f"[EXTRACT DEBUG] Imóvel {idx+1}:")
                    print(f"  - Título: {titulo[:60]}")
                    print(f"  - Preço: {preco}")
                    print(f"  - Link: {link[:70]}")
                    print(f"  - Imagem: {imagem[:70]}")
        
        except Exception as e:
            if debug:
                print(f"[EXTRACT DEBUG] Erro ao processar card {idx}: {e}")
            continue
    
    total_cards = len(cards)
    total_unicos = len(imoveis)
    duplicatas = total_cards - total_unicos
    print(f"[INFO] Página analisada: {total_cards} cards encontrados, "
          f"{total_unicos} imóveis únicos"
          + (f", {duplicatas} duplicata(s) removida(s)" if duplicatas > 0 else ""))

    # Retorna apenas top_n se especificado
    if top_n:
        imoveis = imoveis[:top_n]
        if debug:
            print(f"[EXTRACT DEBUG] Retornando apenas {top_n} imóveis mais recentes")
    
    return imoveis


def carregar_ids_vistos(arquivo='ids_vistos.json'):
    """
    Carrega IDs de imóveis já vistos do arquivo.

    Returns:
        set: Conjunto de IDs já vistos. Vazio se arquivo não existe.
    """
    if not os.path.exists(arquivo):
        return set()
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return set(dados.get('ids', []))
    except Exception:
        return set()


def salvar_ids_vistos(ids, arquivo='ids_vistos.json'):
    """
    Salva IDs de imóveis vistos no arquivo para uso futuro.

    Args:
        ids (set): Conjunto de IDs a salvar.
        arquivo (str): Caminho do arquivo JSON.
    """
    from datetime import datetime
    dados = {
        'ultima_execucao': datetime.now().isoformat(),
        'ids': list(ids)
    }
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def filtrar_novos_imoveis(imoveis, ids_vistos, max_novos=8):
    """
    Filtra imóveis que ainda não foram vistos.

    Args:
        imoveis (list): Lista de imóveis extraídos.
        ids_vistos (set): Conjunto de IDs já vistos.
        max_novos (int): Limite máximo de novos imóveis a retornar.

    Returns:
        list: Lista de imóveis novos, limitada a max_novos.
    """
    novos = []
    ids_novos = set()
    for im in imoveis:
        if im['id'] not in ids_vistos and im['id'] != 'N/A' and im['id'] not in ids_novos:
            ids_novos.add(im['id'])
            novos.append(im)
            if len(novos) == max_novos:
                break
    return novos


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
    from .config import EMAIL_SENDER, EMAIL_RECIPIENT, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
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
                    .imagem-imovel {{
                        width: 100%;
                        max-width: 360px;
                        height: auto;
                        display: block;
                        margin: 0 0 12px 0;
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
            imagem = imovel.get('imagem')
            imagem_html = ""
            if imagem and imagem != 'N/A':
                imagem_segura = escape(imagem, quote=True)
                alt_seguro = escape(imovel.get('titulo', 'Imagem do imóvel'), quote=True)
                imagem_html = f'<img src="{imagem_segura}" alt="{alt_seguro}" class="imagem-imovel">'

            titulo = escape(imovel.get('titulo', 'N/A')[:200], quote=True)
            preco = escape(imovel.get('preco', 'N/A'), quote=True)
            link = escape(imovel.get('link', 'N/A'), quote=True)
            imovel_id = escape(imovel.get('id', 'N/A'), quote=True)

            html_content += f"""
                    <div class="imovel">
                        <div class="numero">#{idx}</div>
                        {imagem_html}
                        <div class="titulo">{titulo}...</div>
                        <div class="preco">{preco}</div>
                        <div><a href="{link}" class="link" target="_blank">Ver anúncio completo →</a></div>
                        <div class="id">ID: {imovel_id}</div>
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
            text_content += f"{idx}. {imovel.get('titulo', 'N/A')[:200]}...\n"
            text_content += f"   Preço: {imovel.get('preco', 'N/A')}\n"
            text_content += f"   Link: {imovel.get('link', 'N/A')}\n"
            text_content += f"   Imagem: {imovel.get('imagem', 'N/A')}\n"
            text_content += f"   ID: {imovel.get('id', 'N/A')}\n\n"
        
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
