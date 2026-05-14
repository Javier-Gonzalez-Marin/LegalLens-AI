from fastapi import FastAPI, UploadFile, File
from abc import ABC, abstractmethod
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class AnalisisResultado(BaseModel):
    puntos_clave: list[str]
    banderas_rojas: list[str]
    riesgo_total: str

class Contrato(ABC):
    def __init__(self, texto: str):
        self.texto = texto

    @abstractmethod
    def obtener_prompt_especifico(self) -> str:
        """Cada hijo define qué buscar [cite: 154]"""
        pass

class ContratoAlquiler(Contrato):
    def obtener_prompt_especifico(self) -> str:
        return "Busca si la fianza es legal (1 mes) y si el inquilino paga averías estructurales." [cite: 164, 165]

class ContratoNDA(Contrato):
    def obtener_prompt_especifico(self) -> str:
        return "Busca si la duración es infinita y si la multa supera los 100.000€." [cite: 168, 169]

@app.post("/api/audit")
async def audit_contract(tipo: str, texto: str):
    if tipo == "alquiler":
        contrato = ContratoAlquiler(texto)
    else:
        contrato = ContratoNDA(texto)
    
    return {"status": "procesado", "tipo": tipo, "prompt_usado": contrato.obtener_prompt_especifico()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
