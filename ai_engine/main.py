import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
from google import genai

try:
    import fitz  
except ImportError:
    fitz = None

app = FastAPI()

# --- CONFIGURACIÓN ---
API_KEY_EXITOSA = "Key" 
client = genai.Client(api_key=API_KEY_EXITOSA)

@app.post("/api/audit")
async def audit_endpoint(tipo: str = Form(...), file: UploadFile = File(...)):
    try:
        contenido_binario = await file.read()
        texto_extraido = ""

        if file.filename.lower().endswith('.pdf') and fitz:
            doc = fitz.open(stream=contenido_binario, filetype="pdf")
            texto_extraido = "".join([p.get_text() for p in doc])
            doc.close()
        else:
            texto_extraido = contenido_binario.decode('utf-8', errors='ignore')

        if not texto_extraido.strip():
            return {"resultado": {"puntos_clave": ["Error"], "banderas_rojas": ["El archivo no contiene texto legible."]}}

        # 2. FASE DE VERIFICACIÓN 
        prompt_verificacion = f"""
        Analiza el inicio de este documento y dime qué tipo de contrato es. 
        Solo responde con una palabra: 'ALQUILER', 'NDA' (si es confidencialidad) o 'DESCONOCIDO'.
        
        TEXTO: {texto_extraido[:2000]}
        """
        
        res_verificacion = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_verificacion
        )
        
        tipo_detectado = res_verificacion.text.strip().upper()
        tipo_seleccionado = tipo.upper() # El que viene del formulario de Django

        # 3. LÓGICA DE VALIDACIÓN CRUZADA
        es_nda = "CONFIDENCIALIDAD" in tipo_seleccionado or "NDA" in tipo_seleccionado
        es_alquiler = "ALQUILER" in tipo_seleccionado or "ARRENDAMIENTO" in tipo_seleccionado

        error_validacion = False
        if es_alquiler and "ALQUILER" not in tipo_detectado:
            error_validacion = True
        elif es_nda and "NDA" not in tipo_detectado:
            error_validacion = True
        
        if error_validacion:
            return {
                "resultado": {
                    "puntos_clave": ["⚠️ Error de validación"],
                    "banderas_rojas": [f"El documento subido no parece ser un {tipo_seleccionado}. La IA detectó que es un documento de tipo: {tipo_detectado}. Por favor, verifica el archivo."]
                }
            }

        # 4. ANÁLISIS 
        prompt_analisis = f"""
        Analiza este contrato de {tipo}. Sé breve y directo.
        
        PUNTOS CLAVE:
        1. [Punto 1]
        2. [Punto 2]
        3. [Punto 3]

        FALLOS Y RIESGOS:
        - [Lista de fallos concretos]
        
        CONTRATO: {texto_extraido[:10000]}
        """

        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_analisis
        )
        
        texto_ia = response.text

        partes = texto_ia.split("FALLOS Y RIESGOS:")
        puntos = partes[0].replace("PUNTOS CLAVE:", "").strip()
        fallos = partes[1].strip() if len(partes) > 1 else "Ninguno detectado"

        return {
            "resultado": {
                "puntos_clave": [p.strip() for p in puntos.split('\n') if p.strip()][:3],
                "banderas_rojas": [f.strip() for f in fallos.split('\n') if f.strip()]
            }
        }

    except Exception as e:
        return {"resultado": {"puntos_clave": ["Error"], "banderas_rojas": [f"Error técnico: {str(e)}"]}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
