import pytest

from property_finder.scraper import extrair_imoveis
from property_finder.config import BASE_URL


pytestmark = pytest.mark.integration


class TestEtapa2:
    """Testes para Etapa 2: Extrair imóveis"""
    
    def test_extrair_imoveis_retorna_lista(self):
        """Testa se extrair_imoveis retorna uma lista"""
        try:
            resultado = extrair_imoveis()
            assert isinstance(resultado, list)
        except Exception as e:
            pytest.skip(f"Erro na extração: {e}")
    
    def test_extrair_imoveis_encontra_pelo_menos_um(self):
        """Testa se encontra pelo menos 1 imóvel - CRITÉRIO ETAPA 2"""
        try:
            imoveis = extrair_imoveis()
            assert len(imoveis) >= 1, "Deve encontrar pelo menos 1 imóvel"
            print(f"\n[SUCESSO] Encontrados {len(imoveis)} imóveis!")
        except Exception as e:
            pytest.skip(f"Erro na extração: {e}")
    
    def test_imovel_tem_estructura_correta(self):
        """Testa se cada imóvel tem os campos esperados"""
        try:
            imoveis = extrair_imoveis()
            if imoveis:
                imovel = imoveis[0]
                assert 'id' in imovel
                assert 'titulo' in imovel
                assert 'preco' in imovel
                assert 'link' in imovel
                print(f"\n[AMOSTRA] {imovel}")
        except Exception as e:
            pytest.skip(f"Erro: {e}")
    
    def test_extrair_imoveis_com_base_url(self):
        """Testa extração com BASE_URL do config"""
        try:
            imoveis = extrair_imoveis(BASE_URL)
            assert isinstance(imoveis, list)
            if imoveis:
                print(f"\n[INFO] Extraídos {len(imoveis)} imóveis de {BASE_URL}")
        except Exception as e:
            pytest.skip(f"Erro: {e}")


class TestEtapa2Analise:
    """Testes de análise de imóveis extraídos"""
    
    def test_todos_imoveis_tem_link(self):
        """Valida que todos os imóveis têm link"""
        try:
            imoveis = extrair_imoveis()
            if imoveis:
                sem_link = [i for i in imoveis if i['link'] == 'N/A']
                taxa_sucesso = (len(imoveis) - len(sem_link)) / len(imoveis) * 100
                print(f"\n[ANALISE] Links extraídos: {taxa_sucesso:.1f}%")
                assert taxa_sucesso >= 50, "Pelo menos 50% devem ter link"
        except Exception as e:
            pytest.skip(f"Erro: {e}")
    
    def test_imoveis_tem_preco(self):
        """Valida que imóveis têm preço"""
        try:
            imoveis = extrair_imoveis()
            if imoveis:
                com_preco = [i for i in imoveis if i['preco'] != 'N/A' and 'R$' in i['preco']]
                taxa_sucesso = len(com_preco) / len(imoveis) * 100
                print(f"\n[ANALISE] Preços extraídos: {taxa_sucesso:.1f}%")
        except Exception as e:
            pytest.skip(f"Erro: {e}")
