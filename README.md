# API OCR Masivo CSJ

Sistema de OCR para procesamiento masivo de PDFs jurídicos del CSJ, desplegado en AWS. CSJ - AWS Cloud

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

# API OCR Masivo CSJ

Sistema de OCR para procesamiento masivo de PDFs jurídicos del CSJ, desplegado en AWS.

## 🚀 URL de Producción
https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc

- **Documentación:** `/docs`
- **Health Check:** `/health`

## 📖 Uso Rápido

### 1. Probar en Navegador
Ir a: https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc/docs

### 2. Probar con Script
```bash
python3 test_api.py
```

### 3. Procesamiento Masivo
```bash
# Editar LISTA_MASIVA_PDFS en procesamiento_masivo.py
python3 procesamiento_masivo.py
```

## 🔧 API Principal

**Endpoint:** `POST /ocr/pdf-to-text-s3`

**Entrada:**
```json
{
  "bucket": "csj-prod-digitalizacion-datalake",
  "pdf_key": "digitalizaciones_csj/caso123/documento.pdf",
  "output_txt_key": "processing/caso123/resources/split_text/documento.txt"
}
```

**Respuesta:**
```json
{
  "message": "OCR completado y .txt subido a S3",
  "pages_processed": 19,
  "time_ocr_process_sec": 49.08
}
```

## 📁 Estructura S3
```
csj-prod-digitalizacion-datalake/
├── digitalizaciones_csj/    # PDFs originales
└── processing/             # Textos extraídos
    └── {caso}/
        └── resources/
            └── split_text/
```

## ⚡ Rendimiento
- **PDF pequeño:** ~30 segundos
- **PDF mediano:** 2-5 minutos
- **PDF grande:** 5-12 minutos

## 🛠️ Desarrollo

**Dependencias:**
```bash
pip install -r requirements.txt
```

**Local:**
```bash
uvicorn app:app --reload
```

**Deployment:**
Push a `main` → Auto-deploy via AWS CodePipeline

## 📦 Archivos
- `app.py` - API principal
- `test_api.py` - Script de pruebas
- `procesamiento_masivo.py` - Procesamiento en lote
- `requirements.txt` - Dependencias