import os
import tempfile
import gc
import re
import uvicorn
import uuid
import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pdf2image import convert_from_path
import pytesseract
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PIL import ImageEnhance, ImageFilter

# Cargar variables de entorno
load_dotenv()

os.environ["TESSDATA_PREFIX"]="/etc/tessdata"

# Configurar AWS S3 - Optimizado para AWS ECS/Fargate con IAM Role
s3_client = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Crear pool de hilos para procesamiento de PDFs
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))  # Ajusta según tu CPU
thread_pool = ThreadPoolExecutor(
    max_workers=MAX_WORKERS,
    thread_name_prefix="pdf_processor"
)


async_tasks = {}

app = FastAPI(
    title="OCR Masivo - AWS Cloud",
    description="API para procesamiento masivo de PDFs con OCR optimizado - Versión AWS ECS",
    version="5.0.0"
)

def get_optimal_config():
    """Configuración optimizada de Tesseract"""
    return r"""--oem 3 --psm 6 -c tessedit_char_whitelist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789ÁÉÍÓÚáéíóúÑñÜü.,;:!?()[]{}"-/\% '"""

def enhance_image_quality(image):
    """Mejora la calidad de imagen para OCR"""
    try:
        # Convertir a escala de grises si no lo está
        if image.mode != 'L':
            image = image.convert('L')
        
        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Aumentar nitidez
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Aplicar filtro para reducir ruido
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    except Exception as e:
        print(f"Error mejorando imagen: {repr(e)}")
        return image

def detect_document_type(text: str) -> str:
    """Detecta el tipo de documento basado en palabras clave"""
    text_lower = text.lower()
    
    if any(keyword in text_lower for keyword in ['camara de comercio', 'certificado de existencia', 'matricula']):
        return 'certificado_comercio'
    elif any(keyword in text_lower for keyword in ['juzgado', 'divorcio', 'sentencia', 'rama judicial']):
        return 'juzgado'
    elif any(keyword in text_lower for keyword in ['certificado de tradicion', 'registro de instrumentos']):
        return 'tradicion'
    else:
        return 'general'

def process_single_page(pdf_path: str, page_num: int) -> str:
    """Procesa una sola página del PDF y retorna el texto extraído de forma optimizada"""
    
    # Primero intentar con pdf2image + OCR
    try:
        images = convert_from_path(
            pdf_path,
            first_page=page_num + 1,
            last_page=page_num + 1,
            thread_count=1,
            grayscale=True,
            size=(2000, None)  # Mayor resolución para mejor calidad
        )
        
        text = ""
        config = get_optimal_config()
        
        if images:
            img = images[0]
            try:
                # Mejorar imagen para OCR
                enhanced_img = enhance_image_quality(img)
                
                # Extraer texto con configuración optimizada
                page_text = pytesseract.image_to_string(enhanced_img, lang="spa", config=config)
                text = page_text
                print(f"✅ OCR exitoso en página {page_num + 1}")
                
            except Exception as e:
                print(f"⚠️ Error en OCR página {page_num + 1}: {repr(e)}")
                text = ""
            
            img.close()
        
        images.clear()
        gc.collect()
        
        if text and text.strip():
            return text
            
    except Exception as pdf2image_error:
        print(f"⚠️ pdf2image falló: {pdf2image_error}")
    
    # Fallback: usar PyPDF2 directamente
    try:
        print(f"💡 Intentando extraer texto directamente del PDF...")
        pdf = PdfReader(pdf_path)
        if page_num < len(pdf.pages):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if text and text.strip():
                print(f"✅ Texto extraído directamente de la página {page_num + 1}")
                return text
        else:
            return ""
    except Exception as pdf_error:
        print(f"❌ Error con PyPDF2: {pdf_error}")
        return ""
    
    return ""

def clean_and_format_text(text: str) -> str:
    """Limpia y formatea el texto extraído de forma optimizada"""
    if not text or not text.strip():
        return ""
    
    # Corregir caracteres mal interpretados comunes
    replacements = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã±': 'ñ', 'Ã¼': 'ü', 'Ãš': 'Ú', 'Ã"': 'Ó', 'Ã': 'Á',
        'Â°': '°', 'Â«': '«', 'Â»': '»', 'â€œ': '"', 'â€': '"',
        'â€™': "'", 'â€˜': "'", 'â€"': '-', 'â€¦': '...', 'Â¡': '¡',
        'Â¿': '¿', 'Ã§': 'ç', 'Ãª': 'ê', 'Ã´': 'ô', 'Ã¢': 'â'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Procesar líneas
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Normalizar espacios múltiples
            line = re.sub(r' +', ' ', line)
            # Mantener caracteres importantes para documentos jurídicos
            line = re.sub(r'[^\w\s\.\,\;\:\?\!\(\)\-\"\'\%\$\°\#\°\/\&\@]', ' ', line)
            line = re.sub(r' +', ' ', line).strip()
            # Filtrar líneas demasiado cortas que probablemente sean ruido
            if len(line) > 2:
                cleaned_lines.append(line)
    
    # Unir líneas manteniendo estructura
    result = '\n'.join(cleaned_lines)
    
    # Limpiar saltos excesivos pero mantener estructura de párrafos
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()

def combine_pages_text(pages_text: List[str]) -> str:
    """Combina el texto de múltiples páginas en un documento cohesivo SIN separadores de página"""
    formatted_pages = []
    
    for i, page_text in enumerate(pages_text):
        if page_text and page_text.strip():
            cleaned_page = clean_and_format_text(page_text)
            if cleaned_page:
                # Solo agregar el texto limpio, SIN separadores de página
                formatted_pages.append(cleaned_page)
    
    return '\n\n'.join(formatted_pages)

def extract_folder_id_from_pdf_name(pdf_key: str) -> str:
    """
    Extrae un ID de carpeta del nombre del PDF basado en la ruta y nombre del archivo
    """
    # Obtener la carpeta padre del PDF (que contiene el ID real)
    path_parts = pdf_key.split('/')
    
    if len(path_parts) >= 3:
        # Para casos como: digitalizaciones_csj/11001310303120020071501/archivo.pdf
        # El folder_id está en la carpeta padre
        folder_name = path_parts[-2]  # Carpeta que contiene el PDF
        
        # Extraer secuencia de números larga de la carpeta
        pattern = re.search(r'(\d{11,})', folder_name)
        if pattern:
            number = pattern.group(1)
            # Para carpetas largas como 11001110200020003182701, retornar completo
            return number
        
        # Buscar patrones de formato YYYY-NNNNN en la carpeta
        pattern_year = re.search(r'(\d{4}-\d{5})', folder_name)
        if pattern_year:
            return pattern_year.group(1)
    
    # Fallback: buscar en el nombre del archivo
    filename = os.path.basename(pdf_key)
    
    # Patrón 1: Formato YYYY-NNNNN (ej: 2008-00151)
    pattern1 = re.search(r'(\d{4}-\d{5})', filename)
    if pattern1:
        return pattern1.group(1)
    
    # Patrón 2: Secuencia larga al inicio del nombre
    pattern2 = re.search(r'^(\d{11,})', filename)
    if pattern2:
        number = pattern2.group(1)
        return number
    
    # Patrón 3: Cualquier secuencia larga de números
    pattern3 = re.search(r'(\d{8,})', filename)
    if pattern3:
        number = pattern3.group(1)
        return number
    
    # Fallback: Usar parte del nombre del archivo
    clean_name = re.sub(r'[^0-9A-Za-z\-]', '-', filename.replace('.pdf', '').replace('.PDF', ''))
    clean_name = re.sub(r'-+', '-', clean_name).strip('-')
    
    return clean_name[:10] if clean_name else "doc-001"

# Modelos Pydantic
class ProcessPDFRequest(BaseModel):
    source_bucket: str
    source_pdf_key: str
    dest_bucket: str
    dest_key: str

class ProcessPDFRequestAsync(BaseModel):
    source_bucket: str
    source_pdf_key: str
    dest_bucket: str
    dest_prefix: str

class ProcessMultiplePDFsRequest(BaseModel):
    source_bucket: str
    pdf_key_list: List[str]
    dest_bucket: str
    dest_prefix: str

class ProcessFolderRequest(BaseModel):
    bucket: str
    folder_prefix: str
    dest_bucket: str
    dest_prefix: str

@app.get("/")
async def root():
    return {
        "message": "API OCR Masivo para Documentos Jurídicos - AWS Cloud",
        "version": "5.0.0",
        "descripcion": "Procesamiento masivo optimizado de PDFs a texto en AWS ECS",
        "endpoints": {
            "process_single_pdf": "/ocr/process-pdf",
            "process_single_pdf_async": "/ocr/process-pdf-async",
            "process_multiple_pdfs": "/ocr/process-multiple",
            "process_folder": "/ocr/process-folder",
            "async_state": "/ocr/async-state/{task_id}",
            "stats": "/ocr/stats/{bucket}/{prefix:path}"
        }
    }

@app.get("/health", status_code=200)
def health_check():
    return JSONResponse(content={"status": "ok", "version": "5.0.0"}, status_code=200)

@app.post("/ocr/process-pdf")
async def process_single_pdf(req: ProcessPDFRequest):
    """Procesa un PDF individual generando un archivo de texto optimizado"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        local_pdf = os.path.join(tmpdir, "input.pdf")
        
        try:
            print(f"🔄 Descargando PDF: {req.source_pdf_key}")
            s3_client.download_file(req.source_bucket, req.source_pdf_key, local_pdf)
            print(f"✅ PDF descargado exitosamente")
        except Exception as e:
            msg = f"Error descargando PDF: {repr(e)}"
            print(msg)
            raise HTTPException(status_code=400, detail=msg)

        try:
            # Obtener número de páginas
            pdf = PdfReader(local_pdf)
            total_pages = len(pdf.pages)
            print(f"📄 PDF tiene {total_pages} páginas")
            
            # Procesar todas las páginas
            all_pages_text = []
            for page_num in range(total_pages):
                try:
                    page_text = process_single_page(local_pdf, page_num)
                    if page_text and page_text.strip():
                        all_pages_text.append(page_text)
                    
                    # Progreso cada 10 páginas
                    if (page_num + 1) % 10 == 0:
                        print(f"✅ Procesadas {page_num + 1}/{total_pages} páginas")
                    
                    # Limpiar memoria periódicamente
                    gc.collect()
                except Exception as e:
                    print(f"Error en página {page_num + 1}: {e}")
                    continue
            
            if not all_pages_text:
                raise HTTPException(status_code=422, detail="No se pudo extraer texto del PDF")
            
            # Combinar todo el texto SIN separadores de página
            document_text = combine_pages_text(all_pages_text)
            
            # Detectar tipo de documento
            doc_type = detect_document_type(document_text)
            
            # Crear archivo de texto con el mismo nombre que el PDF original
            original_filename = os.path.basename(req.source_pdf_key)
            filename = original_filename.replace('.pdf', '.txt').replace('.PDF', '.txt')
            local_txt = os.path.join(tmpdir, filename)
            
            # Escribir contenido
            with open(local_txt, "w", encoding="utf-8") as f:
                f.write(document_text)
            
            # Subir a S3 en la estructura correcta: processing/{folder_id}/resources/split_text/
            s3_key = req.dest_key
            s3_client.upload_file(local_txt, req.source_bucket, s3_key)
            
            print(f"✅ Archivo subido: {s3_key}")
            
            return {
                "status": "success",
                "message": "PDF procesado exitosamente",
                "destination_bucket": req.dest_bucket,
                "destination_key": req.dest_key,
                "total_pages": total_pages,
                "s3_key": s3_key,
                "pages_processed": len(all_pages_text),
                "document_type": doc_type
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error procesando PDF: {e}")

@app.post("/ocr/process-pdf-async")
async def process_single_pdf_async(req: ProcessPDFRequestAsync, background_tasks: BackgroundTasks):
    """Procesa un PDF individual generando un archivo de texto optimizado en segundo plano"""
    
    # Verificar que el archivo existe en S3 antes de procesar
    try:
        s3_client.head_object(Bucket=req.source_bucket, Key=req.source_pdf_key)
        print(f"✅ Archivo encontrado en S3: {req.source_pdf_key}")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado en S3: {req.source_pdf_key}")
        else:
            raise HTTPException(status_code=500, detail=f"Error verificando archivo en S3: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado verificando archivo: {str(e)}")
    
    # Generar UUID único para seguimiento
    task_id = str(uuid.uuid4())
    
    # Inicializar estado en async_tasks
    async_tasks[task_id] = {
        "state": "In Progress",
        "progress": "0/0"
    }
    
    def process_pdf_background():
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                local_pdf = os.path.join(tmpdir, "input.pdf")
                
                try:
                    print(f"🔄 Descargando PDF: {req.source_pdf_key}")
                    s3_client.download_file(req.source_bucket, req.source_pdf_key, local_pdf)
                    print(f"✅ PDF descargado exitosamente")
                except Exception as e:
                    async_tasks[task_id] = {
                        "state": "Error",
                        "progress": "0/0",
                        "error": str(e)
                    }
                    return

                try:
                    # Obtener número de páginas
                    pdf = PdfReader(local_pdf)
                    total_pages = len(pdf.pages)
                    print(f"📄 PDF tiene {total_pages} páginas")
                    
                    # Actualizar progreso inicial
                    async_tasks[task_id]["progress"] = f"0/{total_pages}"
                    
                    # Procesar todas las páginas
                    all_pages_text = []
                    for page_num in range(total_pages):
                        try:
                            page_text = process_single_page(local_pdf, page_num)
                            if page_text and page_text.strip():
                                all_pages_text.append(page_text)
                            
                            # Actualizar progreso
                            async_tasks[task_id]["progress"] = f"{page_num + 1}/{total_pages}"
                            
                            # Progreso cada 10 páginas
                            if (page_num + 1) % 10 == 0:
                                print(f"✅ Procesadas {page_num + 1}/{total_pages} páginas")
                            
                            # Limpiar memoria periódicamente
                            gc.collect()
                        except Exception as e:
                            print(f"Error en página {page_num + 1}: {repr(e)}")
                            continue
                    
                    if not all_pages_text:
                        async_tasks[task_id] = {
                            "state": "Error",
                            "progress": f"{total_pages}/{total_pages}",
                            "error": "No se pudo extraer texto del PDF"
                        }
                        return
                    
                    # Combinar todo el texto SIN separadores de página
                    document_text = combine_pages_text(all_pages_text)
                    
                    # Detectar tipo de documento
                    doc_type = detect_document_type(document_text)
                    
                    # Crear archivo de texto con el mismo nombre que el PDF original
                    original_filename = os.path.basename(req.source_pdf_key)
                    filename = original_filename.replace('.pdf', '.txt').replace('.PDF', '.txt')
                    local_txt = os.path.join(tmpdir, filename)
                    
                    # Escribir contenido
                    with open(local_txt, "w", encoding="utf-8") as f:
                        f.write(document_text)
                    
                    # Subir a S3 en la estructura correcta
                    s3_key = f"{req.dest_prefix}/{filename}"
                    s3_client.upload_file(local_txt, req.source_bucket, s3_key)
                    
                    print(f"✅ Archivo subido: {s3_key}")
                    
                    # Marcar como completado exitosamente
                    async_tasks[task_id] = {
                        "state": "OK",
                        "progress": f"{total_pages}/{total_pages}",
                        "filename": filename,
                        "s3_key": s3_key,
                        "pages_processed": len(all_pages_text),
                        "document_type": doc_type
                    }
                    
                except Exception as e:
                    async_tasks[task_id] = {
                        "state": "Error",
                        "progress": "0/0",
                        "error": str(e)
                    }
                    
        except Exception as e:
            async_tasks[task_id] = {
                "state": "Error",
                "progress": "0/0",
                "error": str(e)
            }
    
    loop = asyncio.get_event_loop()
    
    loop.run_in_executor(thread_pool, process_pdf_background)
    
    return {
        "message": "PDF enviado para procesamiento en segundo plano",
        "task_id": task_id,
        "state": "In Progress"
    }

@app.get("/ocr/async-state/{task_id}")
async def get_async_task_state(task_id: str):
    """Obtiene el estado de una tarea asíncrona por su UUID"""
    
    if task_id not in async_tasks:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task_info = async_tasks[task_id]
    
    if task_info["state"].upper() in ["OK", "ERROR"]:
        task_result = async_tasks.pop(task_id)
        return task_result
        
    return task_info

@app.post("/ocr/process-multiple")
async def process_multiple_pdfs(req: ProcessMultiplePDFsRequest):
    """Procesa múltiples PDFs de una lista específica"""
    
    results = []
    total_pdfs = len(req.pdf_key_list)
    
    print(f"🚀 Iniciando procesamiento masivo de {total_pdfs} PDFs")
    
    for i, pdf_key in enumerate(req.pdf_key_list):
        folder_id = extract_folder_id_from_pdf_name(pdf_key)
        
        print(f"\n📄 Procesando PDF {i+1}/{total_pdfs}: {pdf_key}")
        print(f"📂 Folder ID extraído: {folder_id}")
        
        filename = "".join(pdf_key.split("/")[-1].split(".")[:-1])
        txt_filename = f"{filename}.txt"
        try:
            pdf_req = ProcessPDFRequest(
                source_bucket=req.source_bucket,
                source_pdf_key=pdf_key,
                dest_bucket=req.dest_bucket,
                dest_key=f"{req.dest_prefix}/{txt_filename}"
            )
            
            result = await process_single_pdf(pdf_req)
            results.append({
                "status": "success",
                "pdf": pdf_key,
                "result": result
            })
            print(f"✅ PDF {i+1}/{total_pdfs} procesado exitosamente")
            
        except Exception as e:
            error_msg = str(e)
            results.append({
                "status": "error",
                "pdf": pdf_key,
                "error": error_msg
            })
            print(f"❌ Error procesando {pdf_key}: {error_msg}")
    
    successful = len([r for r in results if r["status"] == "success"])
    
    return {
        "message": "Procesamiento múltiple completado",
        "total_pdfs": total_pdfs,
        "successful": successful,
        "failed": total_pdfs - successful,
        "results": results
    }

@app.post("/ocr/process-folder")
async def process_folder(req: ProcessFolderRequest):
    """Procesa todos los PDFs en una carpeta de S3"""
    try:
        print(f"🔍 Buscando PDFs en carpeta: {req.folder_prefix}")
        
        # Listar PDFs en la carpeta
        paginator = s3_client.get_paginator('list_objects_v2')
        pdfs = []
        
        for page in paginator.paginate(Bucket=req.bucket, Prefix=req.folder_prefix):
            for obj in page.get('Contents', []):
                if obj['Key'].lower().endswith('.pdf'):
                    pdfs.append(obj['Key'])
        
        if not pdfs:
            raise HTTPException(status_code=404, detail=f"No se encontraron PDFs en: {req.folder_prefix}")
        
        print(f"📄 Encontrados {len(pdfs)} PDFs para procesar")
        
        # Usar el endpoint de múltiples PDFs
        multiple_req = ProcessMultiplePDFsRequest(
            source_bucket=req.bucket,
            pdf_key_list=pdfs,
            dest_bucket=req.dest_bucket,
            dest_prefix=req.dest_prefix
        )
        
        return await process_multiple_pdfs(multiple_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando carpeta: {e}")

@app.get("/ocr/stats/{bucket}/{prefix:path}")
async def get_folder_stats(bucket: str, prefix: str):
    """Obtiene estadísticas de una carpeta en S3"""
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        
        total_files = 0
        total_size = 0
        pdf_files = 0
        txt_files = 0
        
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                total_files += 1
                total_size += obj['Size']
                
                if obj['Key'].lower().endswith('.pdf'):
                    pdf_files += 1
                elif obj['Key'].endswith('.txt'):
                    txt_files += 1
        
        return {
            "bucket": bucket,
            "prefix": prefix,
            "statistics": {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "pdf_files": pdf_files,
                "txt_files": txt_files,
                "processed_ratio": f"{txt_files}/{pdf_files}" if pdf_files > 0 else "0/0"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        # Limpiar el pool de hilos al cerrar
        print("🔄 Cerrando ThreadPool...")
        thread_pool.shutdown(wait=True)
        print("✅ ThreadPool cerrado correctamente")
