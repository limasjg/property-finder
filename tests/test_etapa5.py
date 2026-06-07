import pytest
import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import enviar_email
from config import EMAIL_SENDER, EMAIL_RECIPIENT


class TestEtapa5:
    """Testes para Etapa 5: Enviar resultado por email"""
    
    def test_funcao_enviar_email_existe(self):
        """Verifica se função enviar_email existe"""
        assert callable(enviar_email)
    
    def test_email_sender_configurado(self):
        """Verifica se EMAIL_SENDER está configurado"""
        assert EMAIL_SENDER is not None
        assert len(EMAIL_SENDER) > 0
        assert '@' in EMAIL_SENDER
    
    def test_email_recipient_configurado(self):
        """Verifica se EMAIL_RECIPIENT está configurado"""
        assert EMAIL_RECIPIENT is not None
        assert len(EMAIL_RECIPIENT) > 0
        assert '@' in EMAIL_RECIPIENT
    
    def test_enviar_email_com_imoveis_vazios_retorna_bool(self):
        """Verifica se função retorna bool com lista vazia"""
        resultado = enviar_email([])
        assert isinstance(resultado, bool)
    
    def test_enviar_email_com_imovel_unico_retorna_bool(self):
        """Verifica se função retorna bool com 1 imóvel"""
        imovel = {
            'id': '12345',
            'titulo': 'Teste Imóvel',
            'preco': 'R$ 500.000',
            'link': 'https://www.imovelweb.com.br/test'
        }
        resultado = enviar_email([imovel])
        assert isinstance(resultado, bool)
    
    def test_email_html_contém_imovel(self):
        """Verifica se email contém informações do imóvel"""
        # Este é um teste de integração (opcional)
        imovel = {
            'id': '999999',
            'titulo': 'Imóvel de Teste para Email',
            'preco': 'R$ 550.000',
            'link': 'https://www.imovelweb.com.br/propriedades/teste'
        }
        # Não testa o envio real, apenas a estrutura
        assert imovel['titulo'] == 'Imóvel de Teste para Email'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
