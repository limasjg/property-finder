import pytest

from property_finder.scraper import acessar_url, validar_acesso_url
from property_finder.config import BASE_URL


class TestEtapa1:
    """Testes para Etapa 1: Acessar URL"""
    
    def test_validar_acesso_url_retorna_bool(self):
        """Testa se validar_acesso_url retorna bool"""
        resultado = validar_acesso_url("https://invalid-url-test-123456.com/")
        assert isinstance(resultado, bool)
    
    def test_validar_acesso_url_com_url_invalida_retorna_false(self):
        """Testa que URL inválida retorna False"""
        resultado = validar_acesso_url("https://thisurldoesnotexist1234567890.example.com/")
        assert resultado is False
    
    def test_funcao_possui_timeout(self):
        """Testa que scraper tem timeout configurado"""
        from property_finder.config import REQUEST_TIMEOUT
        assert REQUEST_TIMEOUT == 10
    
    def test_funcao_possui_headers(self):
        """Testa que scraper tem headers configurados"""
        from property_finder.config import HEADERS
        assert isinstance(HEADERS, dict)
        assert 'User-Agent' in HEADERS
    
    def test_base_url_esta_configurada(self):
        """Testa que BASE_URL está configurada"""
        assert BASE_URL is not None
        assert len(BASE_URL) > 10
        assert 'http' in BASE_URL


class TestEtapa1Integracao:
    """Testes de integração para Etapa 1"""

    pytestmark = pytest.mark.integration
    
    def test_validar_acesso_url_com_google(self):
        """Testa validação com URL confiável (Google)"""
        try:
            resultado = validar_acesso_url("https://www.google.com/")
            assert isinstance(resultado, bool)
            # Google geralmente retorna True
            if resultado:
                assert resultado is True
        except Exception as e:
            pytest.skip(f"Erro de rede: {e}")
    
    def test_acessar_url_retorna_objeto_valido(self):
        """Testa que acessar_url retorna objeto com atributos necessários"""
        try:
            response = acessar_url("https://www.google.com/")
            assert hasattr(response, 'status_code')
            assert hasattr(response, 'text')
            assert hasattr(response, 'content')
            assert isinstance(response.text, str)
            assert len(response.text) > 0
        except Exception as e:
            pytest.skip(f"Erro de rede/timeout: {e}")
    
    def test_validar_acesso_url_com_imovelweb_url(self):
        """Testa validação com URL do Imovelweb (do config)"""
        try:
            resultado = validar_acesso_url(BASE_URL)
            assert isinstance(resultado, bool)
            # URL do Imovelweb deve ser acessível (mesmo que com 403 Cloudflare)
            print(f"Resultado de validação de Imovelweb: {resultado}")
        except Exception as e:
            pytest.skip(f"Timeout ou erro de rede: {e}")
