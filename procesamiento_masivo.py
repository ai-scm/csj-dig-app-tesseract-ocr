#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Configuración de la API
API_BASE_URL = "https://csj-prod-tesseract.ia.ramajudicial.consultadocumental.nuvu.cc"  # URL AWS ya deployada
BUCKET_NAME = "csj-prod-digitalizacion-datalake"  # Tu bucket de S3

# AQUÍ VA TU LISTA MASIVA DE 224 PDFs - Basado en tu código de ejemplo
LISTA_MASIVA_PDFS = [
    "digitalizaciones_csj/11001203103119890524501/11001203103119890524501 - MINISTERIO DE DEFENSA vs SOFIA PLATA DE PABON TOMO I.PDF",
    "digitalizaciones_csj/11001310004199300043001/11001310004199300043001 - HENRY TORRES LEON vs LUCIA BOTERO DE ROBLEDO - TOMO 2.PDF",
    "digitalizaciones_csj/11001310103020130013400/11001310103020130013400 - MANUEL DARIO MELO ORTIZ vs GERMAN SERNA GIRALDO TOMO III.PDF",
    "digitalizaciones_csj/11001310300319980703401/11001310300319980703401 - FNA vs CAMILO ALFREDO PERDOMO TOMO 01.PDF",
    "digitalizaciones_csj/11001310300319990960301/11001310300319990960301 - FNA vs LIDIA ESPERANZA HERNANDEZ.PDF",
    "digitalizaciones_csj/11001310300319990969201/11001310300319990969201 - LIDIA EMILIA ACOSRTA DE MEJIA vs FLOR AYDE QUITIAN PEÃ'A - TOMO 1.PDF",
    "digitalizaciones_csj/11001310300320020009101/11001310300320020009101 - FNA vs OMAIRA MERCEDES RAMIREZ.PDF",
    "digitalizaciones_csj/11001310300419930008001/11001310300419930008001 - ALBA MARIA MARTINEZ vs ALICIA BOTERO Y OTROS TOMO 01.PDF",
    "digitalizaciones_csj/11001310300419930008001/11001310300419930008001 - ALBA MARIA MARTINEZ vs ALICIA BOTERO Y OTROS TOMO 08.PDF",
    "digitalizaciones_csj/11001310300420030015700/11001310300420030015700 - CENTRAL DE INVERSIONES S.A. vs TULIO GUTIERREZ APONTE TOMO I.PDF",
    "digitalizaciones_csj/11001310300520020354600/11001310300520020354600 - RAFAEL RINCON ORTEGA vs JORGE ENRIQUE RINCON ORTEGA - TOMO 1.PDF",
    "digitalizaciones_csj/11001310300520090075300/11001310300520090075300 - BANCO COLPATRIA vs MIRYAM SERRANO ROA - TOMO 1.PDF",
    "digitalizaciones_csj/11001310300620010100801/11001310300620010100801 TOMO 05.PDF",
    # AGREGAR AQUÍ TUS 224 PDFs RESTANTES...
    # Puedes copiar y pegar tu lista completa aquí
]

def procesar_lote_masivo_completo():
    """Procesa la lista masiva completa de PDFs (224 PDFs)"""
    print("🚀 PROCESAMIENTO MASIVO COMPLETO")
    print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    # Analizar las carpetas únicas
    carpetas_unicas = set()
    for pdf in LISTA_MASIVA_PDFS:
        if '/' in pdf:
            folder_id = pdf.split('/')[1]  # Extraer el folder_id de la ruta
            carpetas_unicas.add(folder_id)
    
    print(f"📄 Total PDFs a procesar: {len(LISTA_MASIVA_PDFS)}")
    print(f"📂 Carpetas diferentes: {len(carpetas_unicas)}")
    print(f"🗂️ Estructura destino: processing/{{folder_id}}/resources/split_text/")
    print()
    
    # Configurar request para procesamiento masivo
    data = {
        "bucket": BUCKET_NAME,
        "pdf_list": LISTA_MASIVA_PDFS
    }
    
    try:
        print("⏳ Enviando solicitud de procesamiento MASIVO al API...")
        print("⚠️  ATENCIÓN: Son muchos PDFs, tomará tiempo considerable")
        print("⏰ Tiempo estimado: 3-6 horas dependiendo del tamaño de cada PDF")
        print("🎯 Cada PDF se guardará automáticamente en su carpeta correcta")
        print()
        
        # Timeout muy largo para procesamiento masivo (8 horas)
        response = requests.post(
            f"{API_BASE_URL}/ocr/process-multiple",
            json=data,
            timeout=28800  # 8 horas de timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PROCESAMIENTO MASIVO COMPLETADO!")
            print(f"📊 Total procesados: {result.get('successful', 0)}/{result.get('total_pdfs', 0)}")
            print()
            
            # Agrupar resultados por carpeta
            resultados_por_carpeta = {}
            errores = []
            
            for pdf_result in result.get('results', []):
                if pdf_result['status'] == 'success':
                    folder_id = pdf_result['result']['folder_id']
                    if folder_id not in resultados_por_carpeta:
                        resultados_por_carpeta[folder_id] = []
                    resultados_por_carpeta[folder_id].append(pdf_result['result'])
                else:
                    errores.append({
                        'pdf': pdf_result['pdf'],
                        'error': pdf_result.get('error', 'Error desconocido')
                    })
            
            # Mostrar resumen por carpeta
            print("📁 RESUMEN POR CARPETA:")
            for folder_id, archivos in resultados_por_carpeta.items():
                print(f"\n📂 Carpeta: {folder_id}")
                print(f"   📍 S3: s3://{BUCKET_NAME}/processing/{folder_id}/resources/split_text/")
                for archivo in archivos:
                    filename = archivo['filename']
                    pages = archivo['pages_processed']
                    print(f"   ✅ {filename} ({pages} páginas)")
            
            # Mostrar errores si los hay
            if errores:
                print(f"\n❌ ERRORES ({len(errores)}):")
                for error in errores[:10]:  # Mostrar solo los primeros 10
                    pdf_name = error['pdf'].split('/')[-1]
                    print(f"   ❌ {pdf_name}: {error['error']}")
                if len(errores) > 10:
                    print(f"   ... y {len(errores) - 10} errores más")
            
            print(f"\n🎉 ¡PROCESAMIENTO MASIVO EXITOSO!")
            print(f"📈 {len(resultados_por_carpeta)} carpetas procesadas correctamente")
            print(f"✅ {result.get('successful', 0)} PDFs procesados exitosamente")
            print(f"❌ {result.get('failed', 0)} PDFs fallaron")
            
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - El procesamiento masivo tomó más de 8 horas")
        print("💡 Esto puede pasar con muchos PDFs grandes")
        print("🔍 Verifica manualmente en S3 cuántos se procesaron exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def procesar_lote_pequeno():
    """Procesa un lote pequeño de prueba (primeros 3 PDFs)"""
    print("🧪 PROCESAMIENTO DE PRUEBA (3 PDFs)")
    print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    # Tomar solo los primeros 3 para prueba
    pdf_list_prueba = LISTA_MASIVA_PDFS[:3]
    
    data = {
        "bucket": BUCKET_NAME,
        "pdf_list": pdf_list_prueba
    }
    
    try:
        print(f"⏳ Procesando {len(pdf_list_prueba)} PDFs de prueba...")
        
        response = requests.post(
            f"{API_BASE_URL}/ocr/process-multiple",
            json=data,
            timeout=3600  # 1 hora para prueba
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prueba completada!")
            print(f"   📊 Exitosos: {result['successful']}/{result['total_pdfs']}")
            
            for pdf_result in result['results']:
                pdf_name = pdf_result['pdf'].split('/')[-1]
                if pdf_result['status'] == 'success':
                    s3_key = pdf_result['result']['s3_key']
                    pages = pdf_result['result']['pages_processed']
                    print(f"   ✅ {pdf_name}: {pages} páginas -> {s3_key}")
                else:
                    print(f"   ❌ {pdf_name}: {pdf_result.get('error', 'Error desconocido')}")
                    
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

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
        print("💡 Asegúrate de que la API esté ejecutándose en puerto 8000")

def main():
    """Función principal"""
    print("🚀 CLIENTE DE PRUEBAS - API OCR MASIVO CSJ")
    print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    # Probar salud de la API
    test_health()
    
    print("\n🎯 OPCIONES DISPONIBLES:")
    print("1. Descomenta 'procesar_lote_pequeno()' para probar con 3 PDFs")
    print("2. Descomenta 'procesar_lote_masivo_completo()' para procesar toda la lista")
    print("3. Agrega más PDFs a LISTA_MASIVA_PDFS para llegar a 224")
    
    # DESCOMENTAR LA FUNCIÓN QUE QUIERAS USAR:
    
    # procesar_lote_pequeno()         # Para prueba con pocos PDFs
    # procesar_lote_masivo_completo() # Para procesar toda la lista masiva
    
    print("\n✨ Para usar:")
    print("   1. Asegúrate de que la API esté corriendo: python app.py")
    print("   2. Configura tus credenciales AWS en .env")
    print("   3. Descomenta la función que quieras ejecutar")

if __name__ == "__main__":
    main()
