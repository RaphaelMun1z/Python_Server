from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import pandas as pd
import os

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Caminho do arquivo CSV
csvFilePath = './resources/Relatorio_cadop.csv'

# Delimitador do CSV
csvDelimiter = ';'

# Encoding do CSV
csvEncoding = 'utf-8'

# Verifica se o arquivo existe
if not os.path.exists(csvFilePath):
    raise FileNotFoundError(f"O arquivo CSV não foi encontrado!")

# Realiza a tentativa de leitura dos dados presentes no CSV
try:
    df = pd.read_csv(csvFilePath, encoding=csvEncoding, delimiter=csvDelimiter)
except Exception as e:
    raise RuntimeError(f"Ocorreu o seguinte erro ao tentar carregar o CSV: {str(e)}")

@app.get("/api/operadora/search-term/", response_model=Dict[str, Any])
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
    
@app.get("/api/operadora/search-ans-register/", response_model=Dict[str, Any])
async def searchByRegistroANS(
    registro_ans: str = Query(..., description="Registro ANS")
) -> Dict[str, Any]:
    try:
        # Realiza a verificação da coluna no DataFrame
        if 'Registro_ANS' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Coluna 'Registro_ANS' não existe!"
            )
        
        # Filtra os dados
        registro_ans = registro_ans.strip()
        resultado = df[df['Registro_ANS'].astype(str).str.strip().str.lstrip('0') == registro_ans.lstrip('0')]
        
        # Verifica se encontrou algum registro
        if resultado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhuma operadora encontrada com o Registro ANS: {registro_ans}"
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