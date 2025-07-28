# Dockerfile para FastAPI + Tesseract OCR + S3

FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       poppler-utils \
       tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto de la API
EXPOSE 8000

# Comando por defecto para desarrollar
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]