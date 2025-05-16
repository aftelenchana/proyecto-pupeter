import requests 
import certifi
import json
import os
import sys
import time  # Importar el módulo para la pausa

# Definir URL de la API
url = "https://guibis.com/home/facturacion/facturacionphp/controladores/emilio"

# Directorio donde está el script
directorio_actual = os.path.dirname(os.path.abspath(__file__))

# Obtener todos los archivos con extensión .jso
archivos_jso = [f for f in os.listdir(directorio_actual) if f.endswith(".jso")]

# Parámetros desde argumentos o valores por defecto
tokenEmpresa = sys.argv[1] if len(sys.argv) > 1 else "1"

# Si no hay archivos .jso, salir
if not archivos_jso:
    print("❌ No se encontraron archivos .jso en la carpeta.")
    sys.exit(1)

# Procesar cada archivo .jso
for archivo_jso in archivos_jso:
    # Renombrar .jso a .json
    archivo_json = archivo_jso.replace(".jso", ".json")
    path_jso = os.path.join(directorio_actual, archivo_jso)
    path_json = os.path.join(directorio_actual, archivo_json)

    # Verificar si el archivo .json ya existe y eliminarlo
    if os.path.exists(path_json):
        os.remove(path_json)

    os.rename(path_jso, path_json)

    try:
        with open(path_json, "r", encoding="utf-8") as json_data:
            data = json.load(json_data)

        # Mostrar los datos que se enviarán
        print(f"\n📤 Enviando archivo: {archivo_json}")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        # Enviar datos a la API (POST)
        response = requests.post(
            url,
            json=data,
            headers={"token": tokenEmpresa, "Content-Type": "application/json"},
            verify=certifi.where()
        )

        # Imprimir respuesta de la API
        print("\n📄 Respuesta de la API:")
        print("Estado HTTP:", response.status_code)
        print("Contenido de la respuesta:", response.text)

        # Intentar convertir la respuesta a JSON si es posible
        try:
            respuestaServer = response.json()
            print("\n📌 Respuesta JSON de la API:")
            print(json.dumps(respuestaServer, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print("⚠️ La respuesta de la API no es un JSON válido.")

        # Eliminar archivos si se reciben respuestas específicas
        if "noticia" in respuestaServer and respuestaServer["noticia"] == "clave_duplicada":
            os.remove(path_json)
            print(f"🗑️ Archivo {archivo_json} eliminado debido a respuesta 'clave_duplicada'.")

        elif "RID.AUTDOC" in respuestaServer:
            os.remove(path_json)
            print(f"🗑️ Archivo {archivo_json} eliminado debido a respuesta con 'RID.AUTDOC'.")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error en la solicitud a la API con el archivo {archivo_json}: {str(e)}")

    except json.JSONDecodeError:
        print(f"\n❌ Error al leer el archivo JSON {archivo_json}. Asegúrate de que esté bien formado.")

    except Exception as e:
        print(f"\n⚠️ Error inesperado con el archivo {archivo_json}: {str(e)}")

    # 🕒 Pausa de 3 segundos después de procesar cada archivo
    print("⏳ Esperando 3 segundos antes de procesar el siguiente archivo...\n")
    time.sleep(3)

print("\n✅ Procesamiento de archivos finalizado.")
