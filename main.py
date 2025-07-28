import os
import tempfile
import gc
from typing import List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from pdf2image import convert_from_path
import pytesseract
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from PyPDF2 import PdfReader

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
AWS_REGION = os.getenv("AWS_REGION")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_SESSION_TOKEN or not AWS_REGION:
    raise RuntimeError("Faltan credenciales AWS en el archivo .env")

# Cliente S3
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_session_token=AWS_SESSION_TOKEN,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

app = FastAPI()

class S3OCRRequest(BaseModel):
    bucket: str
    pdf_key: str
    output_txt_key: str


@app.get("/")
async def root():
    return {"message": "API de OCR con FastAPI y Tesseract"}

def process_page(pdf_path: str, page_num: int, batch_size: int = 3) -> str:
    """Procesa un rango de páginas del PDF y retorna el texto extraído"""
    images = convert_from_path(
        pdf_path,
        first_page=page_num + 1,
        last_page=min(page_num + batch_size, page_num + 1),
        thread_count=2,  # Limitar threads para no sobrecargar la CPU
        grayscale=True,  # Reducir uso de memoria
        size=(1700, None)  # Redimensionar para balance entre calidad y memoria
    )
    
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"
        img.close()  # Liberar memoria de la imagen
    
    images.clear()  # Limpiar lista de imágenes
    gc.collect()  # Forzar recolección de basura
    return text

@app.post("/ocr/pdf-to-text-s3")
async def ocr_pdf_to_text_s3(req: S3OCRRequest, background_tasks: BackgroundTasks):
    """
    Descarga un PDF de S3, lo convierte a imágenes, aplica OCR con Tesseract
    y sube el .txt resultante de nuevo a S3.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        local_pdf = os.path.join(tmpdir, "input.pdf")
        local_txt = os.path.join(tmpdir, "output.txt")
        
        # 1) Descargar PDF desde S3
        try:
            s3_client.download_file(req.bucket, req.pdf_key, local_pdf)
        except (BotoCoreError, ClientError) as e:
            raise HTTPException(status_code=400, detail=f"Error al descargar PDF: {e}")

        try:
            # 2) Obtener número total de páginas
            pdf = PdfReader(local_pdf)
            total_pages = len(pdf.pages)
            
            # 3) Procesar PDF por lotes de páginas
            all_text = []
            batch_size = 3  # Procesar 3 páginas a la vez
            
            for page_num in range(0, total_pages, batch_size):
                try:
                    text = process_page(local_pdf, page_num, batch_size)
                    all_text.append(text)
                    gc.collect()  # Forzar liberación de memoria
                except Exception as e:
                    print(f"Error en página {page_num}: {str(e)}")
                    continue  # Continuar con la siguiente página si hay error
            
            # 4) Guardar resultado en archivo
            with open(local_txt, "w", encoding="utf-8") as f:
                f.write("".join(all_text))
            
            # 5) Subir archivo a S3
            s3_client.upload_file(local_txt, req.bucket, req.output_txt_key)
            
            return {
                "message": "OCR completado y .txt subido a S3",
                "output_txt_key": req.output_txt_key,
                "pages_processed": total_pages
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error durante el procesamiento: {str(e)}"
            )

 