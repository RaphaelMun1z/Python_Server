from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import pandas as pd
import re
import os

app = FastAPI(
    title="API de operadoras de plano de saúde ativas",
    description="API para consulta de operadoras de saúde registradas na ANS",
    version="1.0.0",
    contact={
        "name": "Raphael Muniz Varela",
        "email": "raphaelmunizvarela@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[{
        "name": "operadoras",
        "description": "Operações relacionadas a operadoras de saúde"
    }]
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Caminho do arquivo CSV
csvFilePath = '../resources/Relatorio_cadop.csv'

# Delimitador do CSV
csvDelimiter = ';'

# Encoding do CSV
csvEncoding = 'utf-8'

# Verifica se o arquivo existe
if not os.path.exists(csvFilePath):
    raise FileNotFoundError(f"O arquivo CSV não foi encontrado!")

def to_camel_case(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9]', '_', str(name))
    parts = name.split('_')
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [to_camel_case(col) for col in df.columns]
    return df

# Realiza a tentativa de leitura dos dados presentes no CSV
try:
    df = pd.read_csv(csvFilePath, encoding=csvEncoding, delimiter=csvDelimiter)
    df = normalize_column_names(df)
except Exception as e:
    raise RuntimeError(f"Ocorreu o seguinte erro ao tentar carregar o CSV: {str(e)}")

# Endpoints

# Teste de conexão
@app.get("/")
def root():
    return {"message": "API está funcionando!"}

@app.get("/api/operadora/search-term/", 
         response_model=Dict[str, Any], 
         summary="Busca operadoras por termo textual", 
         description="""Realiza uma busca textual em todas as colunas do dataset de operadoras. Retorna resultados paginados.""", 
         tags=["operadoras"])
async def searchForOperadoras(
    term: str,
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Número de registros por página")
) -> Dict[str, Any]:
    try:
        # Realiza o filtro dos resultados
        term = term.lower()
        resultados = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(term).any(), axis=1)]
        
        # Configura a paginação
        total = len(resultados)
        inicio = (page - 1) * per_page
        fim = inicio + per_page
        
        dados_paginados = resultados.iloc[inicio:fim].to_dict(orient='records')
        
        return {
            "data": dados_paginados,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro durante a busca: {str(e)}")
    
@app.get("/api/operadora/search-ans-register/", 
         response_model=Dict[str, Any],
         summary="Busca operadora por registro ANS",
         description="""Busca uma operadora específica usando seu número de registro na ANS. Retorna todos os detalhes da operadora encontrada.""",
         tags=["operadoras"])
async def searchByRegistroANS(
    registroAns: str = Query(..., description="Registro ANS")
) -> Dict[str, Any]:
    try:
        # Verifica se a coluna existe no DataFrame
        if 'registroAns' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Coluna 'registroAns' não existe!"
            )
        
        # Filtra os dados
        registroAns = registroAns.strip()
        resultado = df[df['registroAns'].astype(str).str.strip().str.lstrip('0') == registroAns.lstrip('0')]
        
        # Verifica se encontrou algum registro
        if resultado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhuma operadora encontrada com o Registro ANS: {registroAns}"
            )
        
        return {
            "success": True,
            "data": resultado.iloc[0].to_dict(),
            "message": "Operadora encontrada com sucesso"
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar pelo Registro ANS: {str(e)}"
        )