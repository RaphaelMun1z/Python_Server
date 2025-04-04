# Teste de nivelamento 04 - Python Server

## Principais recursos tecnologicos utilizados:
 - Framework FastAPI para desenvolver a API
 - Pandas para manipular o CSV
 - Postman para testar as endpoints

## Passo a passo para executar o projeto:

1. Clone o projeto:
git clone https://github.com/RaphaelMun1z/Python_Server.git

2. Acesse o diretório raiz do projeto

3. Instale as dependências:
pip install -r requirements.txt

4. Inicie o servidor utilizando o seguinte comando:
uvicorn server_app:app --reload --port 8000

5. Acesse a documentação Swagger (localmente) em:
http://localhost:8000/docs