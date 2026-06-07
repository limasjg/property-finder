import pytest
import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import extrair_imoveis
from config import BASE_URL


class TestEtapa4:
    """Testes para Etapa 4: Ordenar por data e trazer top 5"""
    
    def test_extrair_imoveis_com_top_5_retorna_lista(self):
        """Verifica se top_n=5 retorna uma lista"""
        imoveis = extrair_imoveis(top_n=5)
        assert isinstance(imoveis, list)
    
    def test_extrair_imoveis_com_top_5_retorna_exatamente_5(self):
        """Verifica se top_n=5 retorna exatamente 5 imóveis"""
        imoveis = extrair_imoveis(top_n=5)
        assert len(imoveis) == 5, f"Esperava 5 imóveis, obteve {len(imoveis)}"
    
    def test_extrair_imoveis_com_top_5_sao_mais_recentes(self):
        """Verifica se top 5 estão na ordem correta (mais recentes primeiro)"""
        todos = extrair_imoveis()
        top5 = extrair_imoveis(top_n=5)
        
        # Verifica se os primeiros 5 de todos são os mesmos que top5
        primeiros_5 = todos[:5]
        
        for idx, (imovel_esperado, imovel_top5) in enumerate(zip(primeiros_5, top5)):
            assert imovel_esperado['id'] == imovel_top5['id'], \
                f"Imóvel {idx+1}: esperava ID {imovel_esperado['id']}, obteve {imovel_top5['id']}"
    
    def test_todos_top_5_tem_estrutura_completa(self):
        """Verifica se todos os top 5 têm campos obrigatórios"""
        imoveis = extrair_imoveis(top_n=5)
        
        for idx, imovel in enumerate(imoveis):
            assert 'id' in imovel, f"Imóvel {idx+1} sem 'id'"
            assert 'titulo' in imovel, f"Imóvel {idx+1} sem 'titulo'"
            assert 'preco' in imovel, f"Imóvel {idx+1} sem 'preco'"
            assert 'link' in imovel, f"Imóvel {idx+1} sem 'link'"
    
    def test_top_5_tem_preco_valido(self):
        """Verifica se todos os top 5 têm preço com R$"""
        imoveis = extrair_imoveis(top_n=5)
        
        for idx, imovel in enumerate(imoveis):
            assert 'R$' in imovel['preco'], \
                f"Imóvel {idx+1} ({imovel['titulo'][:30]}) sem R$ no preço"
    
    def test_top_5_tem_link_valido(self):
        """Verifica se todos os top 5 têm link completo"""
        imoveis = extrair_imoveis(top_n=5)
        
        for idx, imovel in enumerate(imoveis):
            assert imovel['link'].startswith('http'), \
                f"Imóvel {idx+1} com link inválido: {imovel['link'][:30]}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
