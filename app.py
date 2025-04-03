from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import csv
from math import ceil

app = Flask(__name__)

# Configuração do CORS
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Caminho do arquivo CSV
csvFilePath = './resources/Relatorio_cadop.csv'

# Delimitador do CSV
csvDelimiter = ';'

# Carrega os dados do CSV
def loadOperadoras():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_data = dbOperadoras[start_idx:end_idx]
    
    return jsonify({
        "data": paginated_data,
        "total": len(dbOperadoras),
        "page": page,
        "totalPages": ceil(len(dbOperadoras) / limit),
        "limit": limit
    })
    
    # Inicializo a lista de operadoras
    operadorasData = []
    
    # Realizo a verificação se o arquivo existe
    if not os.path.exists(csvFilePath):
        raise FileNotFoundError(f"O arquivo {csvFilePath} não foi encontrado!")
    
    # Tenta abrir o arquivo CSV e ler os dados
    # Se não conseguir, lança uma exceção com a mensagem de erro
    try:
        with open(csvFilePath, 'r', encoding='utf-8') as csvfile:
            fileReader = csv.DictReader(csvfile, delimiter=csvDelimiter)
            operadorasData = [row for row in fileReader]
    except Exception as e:
        raise Exception(f"Não foi possível ler o arquivo CSV: {str(e)}")
    
    # Retorna os dados
    return operadorasData

# Tenta carregar os dados do CSV e inicializa a variável dbOperadoras
try:
    dbOperadoras = loadOperadoras()
except Exception as e:
    print(f"Erro inicial: {str(e)}")
    dbOperadoras = []
        
# Rota para buscar todas as operadoras
@app.route('/api/operadoras', methods=['GET'])
def findAllOperadoras():
    return jsonify(dbOperadoras)

# Rota para buscar operadora por 'CNPJ'
@app.route('/api/operadoras/cnpj/<cnpj>', methods=['GET'])
def findOperadoraByCNPJ(cnpj):
    # Filtra dbOperadoras pelo CNPJ informado
    operadora = [op for op in dbOperadoras if op['CNPJ'] == cnpj]
    
    # Caso não encontre, é retornado o status 404 (Not Found)
    if not operadora:
        return jsonify({"error": "Operadora não encontrada"}), 404
    
    # Retorna a operadora encontrada
    return jsonify(operadora[0])

# Rota para buscar operadora por 'Razão Social'
@app.route('/api/operadoras/razao_social', methods=['POST'])
def findOperadoraByRazaoSocial():
    # Recebe a 'razao_social' pelo JSON enviado no corpo da requisição
    data = request.get_json()
    
    # Verifica se o campo 'razao_social' foi recebido
    if not data or 'razao_social' not in data:
        return jsonify({"error": "O campo 'Razão Social' é obrigatório!"}), 400
    
    razao_social = data['razao_social']

    # Filtra dbOperadoras pela 'Razão Social' informada
    operadora = [op for op in dbOperadoras if 'Razao_Social' in op and op['Razao_Social'].lower() == razao_social.lower()]
    
    # Caso não encontre, é retornado o status 404 (Not Found)
    if not operadora:
        return jsonify({"error": "Operadora não encontrada"}), 404
    
    # Retorna a operadora encontrada
    return jsonify(operadora[0])

app.run(port=5000, host='localhost', debug=True)