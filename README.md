# Property Finder

Monitoramento de anuncios do Imovelweb para Windows, com foco em simplicidade e manutencao.

## O que o sistema faz

- Acessa uma URL configuravel do Imovelweb.
- Extrai os anuncios da primeira pagina.
- Remove duplicatas por **ID** e por **fingerprint** (titulo + preco normalizado).
- Compara com IDs e fingerprints ja vistos.
- Envia por email apenas anuncios novos (maximo de 8).
- Nao envia email quando nao ha novidades.

A deduplicacao dupla detecta imoveis repetidos mesmo quando mudam de ID no site.

## Estrutura

- `main.py`: entrypoint compativel (`python main.py`).
- `src/property_finder/app.py`: fluxo principal.
- `src/property_finder/scraper.py`: extracao, deduplicacao, persistencia e email.
- `src/property_finder/config.py`: configuracoes da aplicacao.
- `tests/`: testes automatizados.
- `data/`: estado local (IDs vistos).
- `output/`: resultados locais da ultima execucao.
- `docs/`: documentacao de apoio.
- `scripts/diagnostics/`: scripts auxiliares de analise/debug.

## Requisitos

- Python 3.10+
- Windows

## Instalacao

```powershell
cd c:\projects\property-finder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
```

## Configuracao

1. Copie `.env.example` para `.env`.
2. Preencha:
- `EMAIL_SENDER`
- `EMAIL_RECIPIENT`
- `EMAIL_PASSWORD` (App Password do Gmail)

## Execucao

```powershell
python main.py
```

## Testes

```powershell
python -m pytest -v
```

## Interface Web (Testes Locais)

Para testar o scraper sem depender de email, use a interface web moderna:

```powershell
python server.py
```

Acesse **http://localhost:5001** e teste:
- Buscar novos imóveis com um clique
- Visualizar resultados em cards modernos
- Ver histórico de buscas anteriores
- Monitorar status em tempo real

Veja [SERVER.md](SERVER.md) para documentação completa da API.

## Comportamento esperado

- Na primeira execucao: considera novos os anuncios encontrados (ate 8).
- Nas proximas: envia somente diferencas.
- Sem diferenca: nao envia email.

## Agendamento no Windows (sabado 07:00)

Exemplo com Task Scheduler:

- Program/script: caminho do `python.exe`
- Add arguments: `c:\projects\property-finder\main.py`
- Trigger: semanal, sabado, 07:00
- Start in: `c:\projects\property-finder`
