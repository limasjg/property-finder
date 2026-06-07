# Como Configurar Email para Property Finder

## 1. Gerar App Password do Gmail

### Passo 1: Ativar 2FA (Autenticação em Duas Etapas)
- Acesse: https://myaccount.google.com/security
- Na seção "Como você se conecta", clique em "Autenticação em duas etapas"
- Siga as instruções para configurar

### Passo 2: Gerar App Password
- Acesse: https://myaccount.google.com/apppasswords
- Selecione:
  - Aplicativo: "Email"
  - Dispositivo: "Windows"
- Clique em "Gerar"
- Copie a senha (16 caracteres)

### Passo 3: Configurar no Arquivo .env

Abra o arquivo `.env` na raiz do projeto:

```
EMAIL_SENDER=seu-email@gmail.com
EMAIL_RECIPIENT=seu-email@gmail.com
EMAIL_PASSWORD=aaaa-bbbb-cccc-dddd
```

**IMPORTANTE:**
- Replace `seu-email@gmail.com` com o seu email real
- Replace `aaaa-bbbb-cccc-dddd` com a App Password copiada (SEM espaços)
- NÃO use sua senha normal do Gmail!

## 2. Testar a Configuração

Execute:
```
python main.py
```

Se tudo estiver configurado corretamente:
- Os 5 imóveis mais recentes serão exibidos no console
- Um email será enviado para o email configurado

## 3. Resolver Problemas Comuns

### Erro: "EMAIL_PASSWORD não configurada!"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Verifique se `EMAIL_PASSWORD` foi preenchido com a App Password

### Erro: "Invalid login credentials"
- A App Password pode estar incorreta
- Gere uma nova em https://myaccount.google.com/apppasswords

### Erro: "SMTPAuthenticationError"
- Gmail pode estar bloqueando a conexão
- Verifique: https://myaccount.google.com/security
- Ative "Acesso de apps menos seguros" (se necessário)

## 4. Usar Outro Provedor de Email

Se preferir outro provedor (Outlook, Yahoo, etc.), altere em `config.py`:

### Outlook/Hotmail:
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
```

### Yahoo:
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
```

## 5. Automação (Windows Task Scheduler)

Depois de testar o email, configure a execução automática:

1. Crie um arquivo `run_property_finder.bat`:
```batch
@echo off
cd C:\projects\property-finder
python main.py
```

2. Abra Task Scheduler (Agendador de Tarefas)
3. Crie uma nova tarefa programada
4. Configure para executar aos sábados às 07:00
5. Aponte para o arquivo `.bat` criado
