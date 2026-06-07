from bs4 import BeautifulSoup
import json
import re

# Ler JSON salvo
with open('resultado_busca.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

imoveis = data['imoveis']

print('IDs em ordem de retorno (primeiros 10):')
for idx, imovel in enumerate(imoveis[:10]):
    id_num = imovel['id']
    titulo = imovel['titulo'][:60]
    datas = re.findall(r'\d{2}/\d{2}/\d{4}', imovel['titulo'])
    data_str = f"Data: {datas[-1]}" if datas else "Sem data"
    print(f'{idx+1}. ID: {id_num} - {data_str}')

print('\n\nIDs em ordem de retorno (últimos 10):')
for idx, imovel in enumerate(imoveis[-10:]):
    id_num = imovel['id']
    titulo = imovel['titulo'][:60]
    datas = re.findall(r'\d{2}/\d{2}/\d{4}', imovel['titulo'])
    data_str = f"Data: {datas[-1]}" if datas else "Sem data"
    print(f'{len(imoveis)-9+idx}. ID: {id_num} - {data_str}')

# Verifica se URL já está ordenada (mais recentes primeiro)
print('\n\nAnálise: A URL está ordenada por "ordem-publicado-maior" (mais recentes primeiro)')
print('Logo, basta retornar os primeiros 5 da lista')
