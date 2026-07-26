# 🚀 Quick Start - Property Finder Web Interface

## 1️⃣ Instalação (primeira vez apenas)

```powershell
# Na pasta do projeto
cd c:\projects\property-finder

# Criar venv (se ainda não tiver)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Instalar Playwright
python -m playwright install chromium
```

## 2️⃣ Rodar o servidor

```powershell
python server.py
```

Você verá:
```
================================================================================
PROPERTY FINDER - Web Server
================================================================================

Acessar em: http://localhost:5000
```

## 3️⃣ Abrir no navegador

Clique em **http://localhost:5000** ou digite na barra de endereço.

## 4️⃣ Testar uma busca

1. Clique no botão **🔎 Buscar Imóveis**
2. Aguarde a busca (pode levar 10-30 segundos na primeira vez)
3. Veja os resultados em cards bonitos
4. Clique em **Ver Anúncio** para visitar o site

## 📊 O que você verá

### Status
```
📍 IDs Conhecidos: 96
🔍 Fingerprints: 45
✓ Última atualização: há 2 dias
```

### Novos Imóveis
```
🏠 Título do Imóvel
💰 R$ 450.000
[Ver Anúncio] ← Clique aqui
```

## 💡 Dicas Úteis

### ✅ Primeira busca
- Todos os imóveis encontrados são considerados "novos"
- Seus IDs e fingerprints são salvos em `data/ids_vistos.json`

### ✅ Buscas subsequentes
- Apenas imóveis novos aparecem
- A deduplicação funciona mesmo se o site muda o ID

### ✅ Ver histórico
- Clique em **📋 Histórico** para ver resultados anteriores
- Sem fazer nova busca (rápido!)

## 🔧 Configurações (Avançado)

### Mudar a URL de busca
Edite `src/property_finder/config.py`:
```python
BASE_URL = "https://seu-url-aqui.com.br"
```

### Ativar email (opcional)
Crie `.env`:
```env
EMAIL_SENDER=seu@gmail.com
EMAIL_PASSWORD=sua_app_password
EMAIL_RECIPIENT=destino@gmail.com
```

Depois customize o servidor para enviar emails quando encontrar novos.

### Debug mode
```powershell
# Ver logs detalhados
$env:FLASK_ENV='development'
python server.py
```

## 📁 Arquivos importantes

```
server.py                    ← O servidor
templates/index.html         ← A interface (HTML + CSS + JS)
data/ids_vistos.json         ← Histórico persistido
output/resultado_busca.json  ← Último resultado
```

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "Porta 5000 já em uso" | `netstat -ano \| findstr :5000` depois `taskkill /PID <PID>` |
| "Falha ao acessar URL" | Verifique sua internet. Pode haver Cloudflare bloqueando. |
| "Nenhum imóvel encontrado" | O site pode ter alterado o layout. Avise ao desenvolvedor. |
| Imagens não carregam | Normal. Nem todos os anúncios têm imagens. |

## 📞 Próximos passos

- ✅ Teste a busca
- ✅ Verifique se os imóveis aparecem corretamente
- ✅ Veja o arquivo `data/ids_vistos.json` (estrutura JSON)
- ✅ Execute novamente para validar deduplicação
- ✅ Quando satisfeito, configure agendamento no Windows Task Scheduler

## 🎉 Sucesso!

Se você conseguiu ver imóveis aparecer no navegador, parabéns! O scraper está funcionando corretamente.

Agora você pode:
1. Usar a interface web para testes rápidos
2. Configurar o `main.py` para rodadas automáticas via Task Scheduler
3. Receber emails com novidades (se configurar)
