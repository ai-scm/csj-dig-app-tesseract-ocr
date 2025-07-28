# Configuración y uso en Linux

Este proyecto expone un servicio REST en FastAPI para aplicar OCR con Tesseract a PDFs almacenados en S3, convirtiéndolos a texto plano y subiéndolos de vuelta a S3.

## Requisitos previos

* Ubuntu (20.04 o superior)
* Python 3.8+
* `poppler-utils` (para convertir PDF a imágenes)
* `tesseract-ocr` (motor OCR)

## Instalación de dependencias del sistema

Abre una terminal y ejecuta:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip poppler-utils tesseract-ocr
```

## Entorno Python

1. Crea y activa un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Instala las dependencias Python:

   ```bash
   pip install --upgrade pip
   pip install fastapi uvicorn pdf2image pytesseract boto3 python-dotenv pillow
   ```

## Variables de entorno

1. Copia la plantilla y configura tus credenciales AWS:

   ```bash
   cp .env.template .env
   ```

2. Abre `.env` y completa los valores:

   ```ini
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   AWS_SESSION_TOKEN=
   AWS_REGION=us-east-1
   ```

## Archivos de ejemplo

* **`.env.template`**: plantilla con las variables necesarias.
* **`request.json`**: ejemplo de body para la petición HTTP:

  ```json
  {
    "bucket": "nombre-del-bucket",
    "pdf_key": "ruta/al/pdf.pdf",
    "output_txt_key": "ruta/de/output.txt"
  }
  ```

## Ejecutar la API

Con el entorno activo y las variables cargadas:

```bash
uvicorn main:app --reload
```

El servicio quedará disponible en `http://localhost:8000`.

## Probar el endpoint con Swagger UI integrada

FastAPI incluye documentación interactiva en:

```
http://localhost:8000/docs
```

Ahí podrás ver el endpoint `/ocr/pdf-to-text-s3`, completar el JSON de ejemplo y ejecutarlo directamente desde la interfaz web.