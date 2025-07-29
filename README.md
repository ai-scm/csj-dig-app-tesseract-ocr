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

## 🎯 URL de Producción

```
https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc
```

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