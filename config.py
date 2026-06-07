# Configuração do projeto
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# URL do Imovelweb para busca de imóveis
BASE_URL = "https://www.imovelweb.com.br/casas-venda-bacacheri-bairro-alto-curitiba-taruma-curitiba-cristo-rei-curitiba-alto-da-xv-curitiba-alto-da-gloria-curitiba-juveve-batel-curitiba-bigorrilho-vila-izabel-curitiba-hugo-lange-jardim-social-curitiba-sao-francisco-curitiba-seminario-curitiba-mais-de-2-quartos-mais-60-m2-util-menos-600000-reales-ordem-publicado-maior.html"

# Timeout para requisições (segundos)
REQUEST_TIMEOUT = 10

# Headers para requisição
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# ========== CONFIGURAÇÃO DE EMAIL ==========
# Gmail SMTP
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Configuração SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
