#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Configuración de la API
API_BASE_URL = "https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc"
BUCKET_NAME = "csj-prod-digitalizacion-datalake"

def test_health():
    """Verifica que la API esté funcionando correctamente"""
    print("Verificando estado de la API...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API funcionando correctamente")
            print(f"  Respuesta: {response.json()}")
            return True
        else:
            print(f"✗ Error en health check: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error conectando a la API: {e}")
        return False

def test_single_pdf():
    """Prueba el procesamiento de un PDF individual"""
    print("\nPROCESAMIENTO DE PDF INDIVIDUAL")
    print("=" * 50)
    
    # Configurar PDF de prueba
    pdf_key = "digitalizaciones_csj/11001310300620010100801/11001310300620010100801 TOMO 04.PDF"
    output_key = "processing/11001310300620010100801/resources/split_text/11001310300620010100801 TOMO 04.txt"
    
    data = {
        "bucket": BUCKET_NAME,
        "pdf_key": pdf_key,
        "output_txt_key": output_key
    }
    
    try:
        print(f"Procesando PDF: {pdf_key}")
        print(f"Resultado se guardará en: {output_key}")
        print("Iniciando procesamiento (esto puede tomar varios minutos)...")
        
        response = requests.post(
            f"{API_BASE_URL}/ocr/pdf-to-text-s3",
            json=data,
            timeout=1800  # 30 minutos timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ PDF procesado exitosamente!")
            print(f"  Páginas procesadas: {result.get('pages_processed', 'N/A')}")
            print(f"  Tiempo OCR: {result.get('time_ocr_process_sec', 'N/A')} segundos")
            print(f"  Archivo guardado: {result.get('output_txt_key', 'N/A')}")
        else:
            print(f"✗ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("✗ Timeout - El PDF tomó más de 30 minutos en procesarse")
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    """Función principal de pruebas"""
    print("API OCR MASIVO CSJ - PRUEBAS")
    print(f"URL: {API_BASE_URL}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Verificar que la API esté funcionando
    if not test_health():
        print("La API no está disponible. Abortando pruebas.")
        return
    
    # Ejecutar prueba de procesamiento
    test_single_pdf()
    
    print("\nPRUEBAS COMPLETADAS")
    print("Para procesamiento masivo, usar: python3 procesamiento_masivo.py")

if __name__ == "__main__":
    main()
