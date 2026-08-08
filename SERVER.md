# 🌐 Property Finder - Web Server

Interface web local moderna para testar e monitorar o scraper de imóveis sem precisar de emails.

## 🚀 Como usar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente (opcional)
Crie um arquivo `.env` na raiz do projeto se quiser configurar email (não é necessário para o servidor web):
```env
EMAIL_SENDER=seu.email@gmail.com
EMAIL_PASSWORD=sua_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Rodar o servidor
```bash
python server.py
```

O servidor iniciará em: **http://localhost:5001**

## 📋 Interface

### Dashboard Principal
- **Status em tempo real**: Mostra quantos IDs e fingerprints estão armazenados
- **Botão Buscar**: Executa o scraper e exibe novos imóveis encontrados
- **Botão Histórico**: Mostra os últimos imóveis encontrados

### Cards de Imóveis
Cada imóvel é exibido em um card moderno com:
- 🖼️ Imagem do imóvel
- 📝 Título descritivo
- 💰 Preço destacado
- 🔗 Link para o anúncio original
- 🆔 ID único para debugging

## 🔧 API Endpoints

### `GET /` 
Retorna a página principal.

### `GET /api/status`
Retorna o status atual:
```json
{
  "success": true,
  "status": {
    "url": "https://www.imovelweb.com.br/...",
    "ids_vistos": 96,
    "fingerprints_vistos": 45,
    "ultimo_resultado": {
      "data_execucao": "2026-07-26T10:00:00",
      "total_novos": 3,
      "imoveis": [...]
    }
  }
}
```

### `POST /api/buscar`
Executa o scraper e retorna novos imóveis:
```json
{
  "success": true,
  "novos": [
    {
      "id": "3040202753",
      "titulo": "Apartamento 2 quartos...",
      "preco": "R$ 380.000",
      "link": "https://www.imovelweb.com.br/...",
      "imagem": "https://..."
    }
  ],
  "total": 1,
  "mensagem": "1 imóvel(is) novo(s) encontrado(s)!"
}
```

### `GET /api/historico`
Retorna o histórico de buscas anteriores:
```json
{
  "success": true,
  "historico": [...],
  "data_execucao": "2026-07-26T10:00:00"
}
```

## 📊 Deduplicação

O servidor usa o sistema de deduplicação baseado em:
1. **ID**: Compatibilidade com histórico anterior
2. **Fingerprint**: Título normalizado + preço (detecta imóveis que mudaram de ID)

Isso evita enviar o mesmo imóvel múltiplas vezes mesmo que o site mude o ID.

## 🎨 Tecnologias

- **Backend**: Flask 2.3+
- **Frontend**: HTML + Tailwind CSS + JavaScript puro
- **Scraping**: Playwright + BeautifulSoup
- **Deduplicação**: Fingerprint (título + preço normalizado)

## 📱 Responsivo

A interface se adapta perfeitamente em:
- 📱 Celular (mobile)
- 💻 Tablet
- 🖥️ Desktop

## 🔍 Debugging

Para ativar modo debug do Flask com auto-reload:
```bash
FLASK_ENV=development python server.py
```

Os logs aparecerão no console, facilitando o debugging de problemas de scraping.

## 📁 Estrutura de Arquivos

```
property-finder/
├── server.py              # Servidor Flask principal
├── templates/
│   └── index.html         # Interface web
├── src/
│   └── property_finder/
│       ├── app.py         # Orquestração do scraper
│       ├── scraper.py     # Lógica de scraping e deduplicação
│       └── config.py      # Configurações
├── data/
│   └── ids_vistos.json    # Histórico de IDs e fingerprints
└── output/
    └── resultado_busca.json # Último resultado da busca
```

## 💡 Dicas

1. **Teste rápido**: Clique em "Buscar Imóveis" para começar
2. **Veja o histórico**: Use "Histórico" para ver buscas anteriores sem fazer nova requisição
3. **Monitore o status**: Os números de IDs e fingerprints aumentam com cada busca
4. **Verifique imagens**: Nem todos os imóveis têm imagens; isso é normal

## ❌ Troubleshooting

**"Falha ao acessar a URL"**
- Verifique sua conexão com a internet
- Pode haver proteção Cloudflare ativa

**"Nenhum imóvel encontrado"**
- O site pode ter alterado o layout HTML
- Verifique os logs do servidor

**CORS / Conexão recusada**
- Certifique-se de que o servidor está rodando na porta 5000
- Tente acessar http://localhost:5001 diretamente

## 📝 Notas

- Os dados são persistidos em `data/ids_vistos.json`
- Cada busca salva o resultado em `output/resultado_busca.json`
- A interface é totalmente frontend (segura - sem credenciais expostas)
