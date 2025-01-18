# E-commerce Site — Django Framework

Este é um projeto completo de e-commerce desenvolvido como portfólio, utilizando o framework Django. Ele inclui funcionalidades para o administrador gerenciar os indicadores da loja, exportar relatórios e processar pagamentos reais através da API do Mercado Pago.

O front-end foi desenvolvido com HTML, CSS, e JavaScript, garantindo uma experiência de usuário interativa e responsiva. Todo o projeto foi criado utilizando a IDE Visual Studio Code, o que facilita o desenvolvimento e a manutenção.

## Funcionalidades

### Painel Administrativo
O administrador pode acessar os indicadores da loja e gerar relatórios para análise de desempenho.

### Pagamentos Reais
Integração com a API do Mercado Pago para processar pagamentos de forma segura.

### Interface Responsiva
Design amigável e adaptável a diferentes dispositivos.


## Tecnologias Utilizadas

- **Backend:** Django, Python
- **Frontend:** HTML, CSS, JavaScript
- **Banco de Dados:** SQLite (configurável para outros bancos)
- **Pagamentos:** API do Mercado Pago

## Pré-requisitos

Antes de começar, certifique-se de ter:

- **Python 3.8+** instalado
- **pip** (gerenciador de pacotes Python)
- **Virtualenv** (opcional, mas recomendado)
- **Visual Studio Code** com as extensões:
  - Python
  - Django
    

## Como Rodar o Projeto

### Clone o Repositório

### Abra no Visual Studio Code

Abra o projeto na IDE com:

```bash
code .
```

### Se Quiser, Crie e Ative um Ambiente Virtual

No terminal integrado do Visual Studio Code:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Instale as Dependências

```bash
pip install -r requirements.txt
```

### Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto e configure:

```env
SECRET_KEY=your_secret_key
DEBUG=True
MERCADO_PAGO_API_KEY=your_api_key
```

### Crie um Superusuário

```bash
python manage.py createsuperuser
```

### Inicie o Servidor de Desenvolvimento

```bash
python manage.py runserver
```


## Como Acessar 

### Painel Administrativo (urls.py)
Acesse [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) com as credenciais do superusuário.

### Aplicação Principal
Acesse [http://127.0.0.1:8000](http://127.0.0.1:8000).

# Há um Banco para Testes
### Caso Não Queira: (https://docs.djangoproject.com/en/5.1/topics/migrations/)


# Imagens

![image1](https://github.com/user-attachments/assets/3f051861-ccb0-486d-b22e-a8107120a444)

![image2](https://github.com/user-attachments/assets/02e4723e-5521-4ffb-8442-72f197699999)

![image3](https://github.com/user-attachments/assets/6b9fc023-862a-4748-869b-343d64e44445)

![image44](https://github.com/user-attachments/assets/e125cf34-3627-4ddf-8c94-dc3c24d2b0a9)

![image5](https://github.com/user-attachments/assets/68609c44-1fdc-45dd-9fbc-077f693c985e)

![image6](https://github.com/user-attachments/assets/53bdd998-df72-49e3-8b92-a67f4e727a3b)
