#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Configuración de la API - AWS Cloud
API_BASE_URL = "https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc"
BUCKET_NAME = "csj-prod-digitalizacion-datalake"

def test_health():
    """Prueba el endpoint de salud"""
    print("🏥 Probando endpoint de salud...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API funcionando correctamente")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Error en health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando a la API: {e}")

def test_single_pdf():
    """Prueba la función 1: Procesar PDF individual con el archivo que mencionaste"""
    print("\n📄 FUNCIÓN 1: Procesar PDF individual")
    print("=" * 50)
    
    # PDF específico que ya está subido
    pdf_key = "digitalizaciones_blend/2008-00151/2008-00151 T010.pdf"
    
    data = {
        "bucket": BUCKET_NAME,
        "pdf_key": pdf_key,
        "folder_id": "2008-00151"  # Extraído del path
    }
    
    try:
        print(f"⏳ Procesando PDF: {pdf_key}")
        print(f"🎯 Se guardará en: s3://{BUCKET_NAME}/processing/2008-00151/resources/split_text/")
        
        response = requests.post(
            f"{API_BASE_URL}/ocr/process-pdf",
            json=data,
            timeout=1800  # 30 minutos
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF procesado exitosamente!")
            print(f"   📂 Folder ID: {result['folder_id']}")
            print(f"   📄 Páginas: {result['total_pages']}")
            print(f"   📝 Archivo: {result['filename']}")
            print(f"   📍 S3 Key: {result['s3_key']}")
            print(f"   🔍 Tipo documento: {result['document_type']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Detalle: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El PDF tomó mucho tiempo en procesarse")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multiple_pdfs():
    """Prueba la función 2: Procesar múltiples PDFs"""
    print("\n📄 FUNCIÓN 2: Procesar múltiples PDFs")
    print("=" * 50)
    
    # Lista de PDFs de ejemplo - usando archivos reales ya subidos
    pdf_list = [
        "digitalizaciones_blend/2008-00151/2008-00151 T010.pdf",
        # Agregar más PDFs aquí cuando estén disponibles
    ]
    
    data = {
        "bucket": BUCKET_NAME,
        "pdf_list": pdf_list
    }
    
    try:
        print(f"⏳ Procesando {len(pdf_list)} PDFs de la lista...")
        
        response = requests.post(
            f"{API_BASE_URL}/ocr/process-multiple",
            json=data,
            timeout=3600  # 1 hora para prueba
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Procesamiento múltiple completado!")
            print(f"   📊 Exitosos: {result['successful']}/{result['total_pdfs']}")
            print(f"   ❌ Fallidos: {result['failed']}")
            
            # Mostrar resumen
            for pdf_result in result['results']:
                if pdf_result['status'] == 'success':
                    pdf_name = pdf_result['pdf'].split('/')[-1]
                    folder_id = pdf_result['result']['folder_id']
                    print(f"   ✅ {pdf_name} -> processing/{folder_id}/resources/split_text/")
                else:
                    pdf_name = pdf_result['pdf'].split('/')[-1]
                    print(f"   ❌ {pdf_name}: {pdf_result.get('error', 'Error desconocido')}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Detalle: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Tomó más tiempo del esperado")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_folder_processing():
    """Prueba la función 3: Procesar carpeta completa"""
    print("\n📂 FUNCIÓN 3: Procesar carpeta completa")
    print("=" * 50)
    
    # Carpeta de ejemplo - usando carpeta real
    folder_prefix = "digitalizaciones_blend/2008-00151/"
    
    data = {
        "bucket": BUCKET_NAME,
        "folder_prefix": folder_prefix
    }
    
    try:
        print(f"⏳ Procesando todos los PDFs en carpeta: {folder_prefix}")
        
        response = requests.post(
            f"{API_BASE_URL}/ocr/process-folder",
            json=data,
            timeout=7200  # 2 horas
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Carpeta procesada completamente!")
            print(f"   📊 Exitosos: {result['successful']}/{result['total_pdfs']}")
            print(f"   ❌ Fallidos: {result['failed']}")
            
            # Mostrar algunos resultados
            success_count = 0
            for pdf_result in result['results']:
                if pdf_result['status'] == 'success' and success_count < 3:
                    pdf_name = pdf_result['pdf'].split('/')[-1]
                    s3_key = pdf_result['result']['s3_key']
                    print(f"   ✅ {pdf_name} -> {s3_key}")
                    success_count += 1
                    
            if result['successful'] > 3:
                print(f"   ... y {result['successful'] - 3} archivos más")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Detalle: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Tomó más tiempo del esperado")
    except Exception as e:
        print(f"❌ Error: {e}")

def get_stats():
    """Obtiene estadísticas de una carpeta"""
    print("\n📊 ESTADÍSTICAS")
    print("=" * 50)
    
    # Ejemplo de carpeta para estadísticas
    bucket = BUCKET_NAME
    prefix = "processing/2008-00151/resources/split_text/"
    
    try:
        response = requests.get(f"{API_BASE_URL}/ocr/stats/{bucket}/{prefix}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"📂 Carpeta: {stats['prefix']}")
            print(f"📄 Archivos totales: {stats['statistics']['total_files']}")
            print(f"📊 Tamaño total: {stats['statistics']['total_size_mb']} MB")
            print(f"📰 PDFs: {stats['statistics']['pdf_files']}")
            print(f"📝 TXTs: {stats['statistics']['txt_files']}")
            print(f"🎯 Ratio procesado: {stats['statistics']['processed_ratio']}")
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal de pruebas"""
    print("🌩️ PROBANDO API OCR MASIVO CSJ - AWS CLOUD")
    print(f"🔗 URL: {API_BASE_URL}")
    print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    # 1. Probar salud de la API
    test_health()
    
    # 2. Descomenta las funciones que quieras probar:
    
    # test_single_pdf()         # Función 1: PDF individual (tu archivo específico)
    # test_multiple_pdfs()      # Función 2: Lista de PDFs  
    # test_folder_processing()  # Función 3: Carpeta completa
    # get_stats()              # Estadísticas
    
    print("\n🎯 INSTRUCCIONES:")
    print("   1. Descomenta las funciones que quieras probar")
    print("   2. Para procesamiento masivo, usa procesamiento_masivo.py")
    print("   3. Todo funciona directo en AWS - no necesitas nada local")
    print("\n🚀 ¡La API está lista en la nube!")

if __name__ == "__main__":
    main()
