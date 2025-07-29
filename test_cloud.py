#!/usr/bin/env python3

import requests
import time
from datetime import datetime

# URL de tu instancia AWS ya deployada
API_URL = "https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc"
BUCKET_NAME = "csj-prod-digitalizacion-datalake"

def test_cloud_health():
    """Prueba que la API en AWS esté funcionando"""
    print("🌥️ PRUEBA DE SALUD - INSTANCIA AWS")
    print("=" * 60)
    print(f"🔗 URL: {API_URL}")
    print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        print("⏳ Verificando endpoint de salud...")
        response = requests.get(f"{API_URL}/health", timeout=30)
        
        if response.status_code == 200:
            print("✅ API está ACTIVA y respondiendo")
            print(f"📊 Respuesta: {response.json()}")
        else:
            print(f"⚠️ API responde pero con código: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API")
        print("💡 Verifica que la instancia esté corriendo en AWS")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La API tardó más de 30 segundos en responder")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_cloud_endpoints():
    """Prueba los endpoints principales"""
    print("\n🎯 PRUEBA DE ENDPOINTS")
    print("=" * 60)
    
    try:
        print("⏳ Probando endpoint raíz...")
        response = requests.get(f"{API_URL}/", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint raíz funciona")
            print(f"📋 Versión: {data.get('version', 'No especificada')}")
            print(f"📝 Descripción: {data.get('descripcion', 'No disponible')}")
            
            if 'endpoints' in data:
                print("\n📌 Endpoints disponibles:")
                for name, path in data['endpoints'].items():
                    print(f"   • {name}: {path}")
        else:
            print(f"⚠️ Problema con endpoint raíz: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando endpoints: {e}")

def test_cloud_ocr_simple():
    """Prueba el procesamiento OCR simple con el PDF que mencionaste"""
    print("\n📄 PRUEBA OCR - PDF ESPECÍFICO")
    print("=" * 60)
    print(f"📁 Archivo: digitalizaciones_blend/2008-00151/2008-00151 T010.pdf")
    print(f"🎯 Folder ID: 2008-00151")
    print()
    
    data = {
        "bucket": BUCKET_NAME,
        "pdf_key": "digitalizaciones_blend/2008-00151/2008-00151 T010.pdf",
        "folder_id": "2008-00151"
    }
    
    try:
        print("⏳ Enviando solicitud de procesamiento OCR...")
        print("⚠️ ATENCIÓN: Esto puede tomar varios minutos dependiendo del tamaño del PDF")
        
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/ocr/process-pdf",
            json=data,
            timeout=1800  # 30 minutos de timeout
        )
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ¡PROCESAMIENTO EXITOSO! ({duration:.1f} segundos)")
            print(f"📊 Páginas procesadas: {result.get('pages_processed', 'N/A')}")
            print(f"📁 Archivo generado: {result.get('filename', 'N/A')}")
            print(f"🔗 S3 Key: {result.get('s3_key', 'N/A')}")
            print(f"📋 Tipo documento: {result.get('document_type', 'N/A')}")
            
            print(f"\n🎉 ¡ÉXITO! El archivo procesado está en:")
            print(f"   s3://{BUCKET_NAME}/{result.get('s3_key', 'N/A')}")
            
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - El procesamiento tomó más de 30 minutos")
        print("💡 Para PDFs muy grandes, esto puede ser normal")
        print("🔍 Verifica manualmente en S3 si se generó el archivo")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def get_cloud_stats():
    """Obtiene estadísticas de la carpeta en S3"""
    print("\n📊 ESTADÍSTICAS DE CARPETA")
    print("=" * 60)
    
    try:
        print("⏳ Obteniendo estadísticas...")
        response = requests.get(
            f"{API_URL}/ocr/stats/{BUCKET_NAME}/digitalizaciones_blend/2008-00151/",
            timeout=60
        )
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Estadísticas obtenidas:")
            print(f"📁 Carpeta: {stats.get('prefix', 'N/A')}")
            
            statistics = stats.get('statistics', {})
            print(f"📄 Total archivos: {statistics.get('total_files', 0)}")
            print(f"💾 Tamaño total: {statistics.get('total_size_mb', 0)} MB")
            print(f"📕 PDFs: {statistics.get('pdf_files', 0)}")
            print(f"📝 TXTs: {statistics.get('txt_files', 0)}")
            print(f"📈 Ratio procesado: {statistics.get('processed_ratio', '0/0')}")
            
        else:
            print(f"⚠️ Error obteniendo estadísticas: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Ejecuta todas las pruebas en la nube"""
    print("🌩️ SUITE DE PRUEBAS - AWS CLOUD")
    print("🚀 API OCR Masivo CSJ - Instancia en AWS")
    print("=" * 80)
    print(f"🕒 Iniciado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # 1. Verificar que la API esté funcionando
    if not test_cloud_health():
        print("\n❌ La API no está disponible. Verifica el deployment.")
        return
    
    # 2. Probar endpoints básicos
    test_cloud_endpoints()
    
    # 3. Obtener estadísticas de la carpeta
    get_cloud_stats()
    
    # 4. Procesar el PDF específico
    print("\n" + "="*80)
    print("🎯 ¿PROCESAR EL PDF AHORA?")
    print("   digitalizaciones_blend/2008-00151/2008-00151 T010.pdf")
    print("⚠️  Esto puede tomar varios minutos...")
    
    user_input = input("\n¿Continuar? (y/n): ").lower().strip()
    if user_input in ['y', 'yes', 's', 'si']:
        test_cloud_ocr_simple()
    else:
        print("⏭️ Procesamiento OCR omitido")
    
    print(f"\n🏁 Pruebas completadas: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
