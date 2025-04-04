# Teste de nivelamento 04 - Python Server

## Principais recursos tecnologicos utilizados:
 - Framework FastAPI para desenvolver a API
 - Pandas para manipular o CSV
 - Postman para testar as endpoints

## Passo a passo para executar o projeto:

1. Clone o projeto:
git clone https://github.com/RaphaelMun1z/Python_Server.git

2. Instale as dependências:
pip install fastapi pandas uvicorn

3. Inicie o servidor utilizando o seguinte comando:
uvicorn server_app:app --reload

4. Acesse a documentação Swagger em:
http://localhost:8000/docs