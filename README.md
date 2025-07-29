# 🚀 API OCR Masivo CSJ - AWS Cloud

API FastAPI para procesamiento masivo de PDFs con OCR Tesseract optimizado, desplegada en **AWS ECS/Fargate** para máximo rendimiento.

## ✨ Características V5.0.0

- 🌩️ **100% Cloud** - Optimizado para AWS ECS/Fargate
- ⚡ **3 Funciones principales** para diferentes casos de uso
- 🎯 **Auto-extracción** de folder_id desde rutas de archivos
- 📊 **Estructura optimizada CSJ**: `processing/{folder_id}/resources/split_text/`
- 🔍 **Detección automática** de tipos de documento jurídico
- 💾 **Gestión inteligente** de memoria para PDFs grandes
- � **Fallback PyPDF2** si falla pdf2image/Tesseract

# API OCR Masivo CSJ - AWS Cloud

API FastAPI para procesamiento masivo de PDFs con OCR Tesseract optimizado, desplegada en AWS ECS/Fargate.

## Información del Deployment

**URL de Producción:** https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc

**Documentación API:**
- Swagger UI: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/docs
- ReDoc: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/redoc
- Health Check: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/health

## Endpoints Disponibles

### 1. Procesar PDF Individual
**Endpoint:** `POST /ocr/pdf-to-text-s3`

Procesa un PDF específico y guarda el resultado en S3.

**Parámetros:**
```json
{
  "bucket": "csj-prod-digitalizacion-datalake",
  "pdf_key": "digitalizaciones_csj/11001310300620010100801/11001310300620010100801 TOMO 04.PDF",
  "output_txt_key": "processing/11001310300620010100801/resources/split_text/11001310300620010100801 TOMO 04.txt"
}
```

**Respuesta exitosa:**
```json
{
  "message": "OCR completado y .txt subido a S3",
  "output_txt_key": "processing/11001310300620010100801/resources/split_text/11001310300620010100801 TOMO 04.txt",
  "pages_processed": 19,
  "time_download_pdf_sec": 0.62,
  "time_ocr_process_sec": 49.08
}
```

## Casos de Uso

### Opción 1: Usar la Documentación Web (Swagger)

1. Acceder a: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/docs
2. Buscar el endpoint `POST /ocr/pdf-to-text-s3`
3. Hacer clic en "Try it out"
4. Introducir los parámetros JSON
5. Hacer clic en "Execute"

### Opción 2: Procesar desde Script Local

Usar el script `test_api.py` incluido en este repositorio:

```bash
python3 test_api.py
```

El script incluye configuración para probar PDFs individuales y verificar el estado de la API.

### Opción 3: Procesamiento Masivo

Para procesar múltiples PDFs, editar el archivo `procesamiento_masivo.py`:

1. Agregar los PDFs a la lista `LISTA_MASIVA_PDFS`:
```python
LISTA_MASIVA_PDFS = [
    "digitalizaciones_csj/11001203103119890524501/11001203103119890524501 - MINISTERIO DE DEFENSA vs SOFIA PLATA DE PABON TOMO I.PDF",
    "digitalizaciones_csj/11001310004199300043001/11001310004199300043001 - HENRY TORRES LEON vs LUCIA BOTERO DE ROBLEDO - TOMO 2.PDF",
    # ... agregar más PDFs aquí
]
```

2. Ejecutar el script:
```bash
python3 procesamiento_masivo.py
```

## Estructura de Archivos S3

```
s3://csj-prod-digitalizacion-datalake/
├── digitalizaciones_csj/          # PDFs originales
│   └── {numero_caso}/
│       └── archivo_original.pdf
└── processing/                    # Resultados procesados
    └── {numero_caso}/
        └── resources/
            └── split_text/
                └── archivo_procesado.txt
```

## Arquitectura

**Infraestructura:**
- AWS ECS/Fargate (contenedores serverless)
- Application Load Balancer
- Amazon ECR (registro de imágenes Docker)
- AWS CodePipeline (CI/CD automático)

**Tecnologías:**
- FastAPI (framework web)
- Tesseract OCR (extracción de texto)
- pdf2image + Pillow (procesamiento de imágenes)
- boto3 (cliente AWS S3)

## Rendimiento

- **PDF pequeño** (1-10 páginas): 15-30 segundos
- **PDF mediano** (50-100 páginas): 2-5 minutos  
- **PDF grande** (200+ páginas): 5-12 minutos
- **Lote masivo**: Procesamiento paralelo optimizado

## Desarrollo y Deployment

### Configuración Local

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno en `.env`
4. Ejecutar localmente: `uvicorn app:app --reload`

### Deployment en AWS

El deployment es automático via AWS CodePipeline:

1. Hacer cambios al código
2. Commit y push a la rama `main`
3. AWS CodePipeline detecta el cambio
4. Construye la imagen Docker automáticamente
5. Despliega a ECS/Fargate (5-10 minutos)

### Verificar Deployment

```bash
curl https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/health
```

## Archivos del Proyecto

- `app.py` - Aplicación principal FastAPI
- `Dockerfile` - Configuración del contenedor
- `requirements.txt` - Dependencias Python
- `test_api.py` - Script de pruebas
- `procesamiento_masivo.py` - Script para procesamiento masivo
- `.env.template` - Plantilla de variables de entorno

## Configuración de Permisos

La aplicación requiere permisos IAM para acceder a S3:
- `s3:GetObject` - Leer PDFs
- `s3:PutObject` - Escribir archivos TXT
- `s3:ListBucket` - Listar contenido del bucket

## Troubleshooting

**Error 403 Forbidden:** Verificar permisos IAM del role de ECS
**Timeout:** PDFs muy grandes pueden requerir más tiempo de procesamiento
**Error 404:** Verificar que el PDF existe en la ruta especificada del bucket

## Contacto

Para soporte técnico o dudas sobre el deployment, consultar la documentación interactiva en Swagger UI.

### 📖 Documentación Interactiva
- **Swagger UI**: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/docs
- **ReDoc**: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/redoc
- **Health Check**: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/health

## 🎯 Las 3 Funciones Principales

### 1️⃣ **Función 1: Procesar PDF Individual**
**Endpoint**: `POST /ocr/process-pdf`

Para procesar un PDF específico:

```json
{
  "bucket": "csj-prod-digitalizacion-datalake",
  "pdf_key": "digitalizaciones_blend/2008-00151/2008-00151 T010.pdf", 
  "folder_id": "2008-00151"
}
```

**Resultado**: 
- Archivo guardado en: `s3://bucket/processing/2008-00151/resources/split_text/2008-00151 T010.txt`

### 2️⃣ **Función 2: Procesar Lista Masiva**
**Endpoint**: `POST /ocr/process-multiple`  

Para procesar múltiples PDFs de diferentes carpetas:

```json
{
  "bucket": "csj-prod-digitalizacion-datalake",
  "pdf_list": [
    "digitalizaciones_csj/11001310300320020009101/archivo1.pdf",
    "digitalizaciones_csj/11001310300420030015700/archivo2.pdf", 
    "digitalizaciones_blend/2008-00151/2008-00151 T010.pdf"
  ]
}
```

**Resultado**:
- Cada PDF se guarda automáticamente en su carpeta correspondiente
- Procesamiento paralelo optimizado 

### 3️⃣ **Función 3: Procesar Carpeta Completa**
**Endpoint**: `POST /ocr/process-folder`

Para procesar todos los PDFs de una carpeta:

```json
{
  "bucket": "csj-prod-digitalizacion-datalake",
  "folder_prefix": "digitalizaciones_blend/2008-00151/"
}
```

**Resultado**:
- Procesa automáticamente todos los PDFs encontrados en la carpeta

## 📊 Endpoint de Estadísticas

**Endpoint**: `GET /ocr/stats/{bucket}/{prefix}`

Ejemplo: 
```
GET /ocr/stats/csj-prod-digitalizacion-datalake/processing/2008-00151/
```

Muestra estadísticas de archivos procesados vs pendientes.

## 🧪 Scripts de Prueba

### Prueba Individual (Archivo de ejemplo ya subido)
```python
# test_api.py
/home/lenovo/Escritorio/Repos/OCR/.venv/bin/python test_api.py
```

### Procesamiento Masivo (Tu lista de 224+ PDFs)
```python  
# procesamiento_masivo.py
/home/lenovo/Escritorio/Repos/OCR/.venv/bin/python procesamiento_masivo.py
```

## 🔄 Proceso de Deploy

### Cuando hagas cambios al código:

1. **Hacer commit y push**:
```bash
git add .
git commit -m "Actualización OCR v5.0.0 - Optimizado para AWS"
git push origin main
```

2. **Rebuild automático**: 
   - AWS CodePipeline detecta el push
   - Construye nueva imagen Docker automáticamente 
   - Redeploy en ECS/Fargate
   - **Tiempo estimado**: 5-10 minutos

3. **Verificar deploy**:
```bash
curl https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/health
```

## 📈 Rendimiento Esperado en AWS

- **PDF pequeño** (1-10 páginas): 15-30 segundos ⚡
- **PDF mediano** (50-100 páginas): 2-5 minutos ⚡  
- **PDF grande** (200+ páginas): 5-12 minutos ⚡
- **Lote masivo 224 PDFs**: 2-4 horas ⚡ (vs 6+ horas local)

## 🗂️ Estructura de Archivos S3

```
s3://csj-prod-digitalizacion-datalake/
├── digitalizaciones_csj/
│   └── {numero_caso}/
│       └── archivo_original.pdf
├── digitalizaciones_blend/
│   └── {folder_id}/
│       └── archivo_original.pdf  
└── processing/
    └── {folder_id}/
        └── resources/
            └── split_text/
                └── archivo_procesado.txt
```

## 🔐 Configuración AWS

La aplicación usa **IAM Role** automáticamente en ECS. No requiere credenciales hardcoded.

**Permisos requeridos**:
- `s3:GetObject` (leer PDFs)
- `s3:PutObject` (escribir TXTs) 
- `s3:ListBucket` (listar carpetas)

## 🚀 Casos de Uso

### ✅ Para 1 PDF específico:
Usar **Función 1** desde Swagger UI

### ✅ Para lista masiva (tu caso de 224 PDFs):
1. Editar `procesamiento_masivo.py`
2. Agregar tu lista completa en `LISTA_MASIVA_PDFS` 
3. Ejecutar el script

### ✅ Para carpeta completa:
Usar **Función 3** con el `folder_prefix`

## 🎉 ¡Todo listo para producción!

La API está optimizada para trabajar 100% en la nube AWS con el poder de procesamiento de ECS/Fargate. 

**¿Siguiente paso?** ¡Probar con el PDF que mencionas y luego escalar al procesamiento masivo! 🚀