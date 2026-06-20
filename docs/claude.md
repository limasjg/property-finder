# Objetivo

Criar um sistema Python para Windows que monitore imóveis do Imovelweb.

# Requisitos

- Código simples.
- Sem overengineering.
- Poucos arquivos.
- Fácil manutenção.

# Tecnologias

Preferência:

- requests
- beautifulsoup4

Somente usar Selenium ou Playwright se necessário.

# Funcionalidades

1. Ler URL configurável.
2. Buscar imóveis.
3. Extrair dados.
4. Ordenar pelos mais recentes.
5. Retornar os 5 mais recentes.
6. Remover duplicados.
7. Permitir execução automática aos sábados às 07:00.

# Estrutura

main.py
scraper.py
config.py
tests/

# Processo obrigatório

Cada etapa deve:

1. Ser implementada.
2. Possuir teste.
3. Ser validada.
4. Só então avançar.

# Etapas

## Etapa 1
Acessar URL.

Critério:
HTTP 200.

## Etapa 2
Extrair imóveis.

Critério:
Encontrar pelo menos 1 imóvel.

## Etapa 3
Extrair dados.

Critério:
Título, preço e link válidos.

## Etapa 4
Ordenar por data.

Critério:
5 mais recentes corretos.

## Etapa 5
Enviar o resultado por email.