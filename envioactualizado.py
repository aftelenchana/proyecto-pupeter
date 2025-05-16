import requests
import json
import sys
import time
import logging
import certifi

# Configuración de logging para mayor depuración
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de variables
url = "https://guibis.com/home/facturacion/facturacionphp/controladores/emilio"
tiempoActual = time.strftime("%c")
logfile = 'pdoc-' + time.strftime("%Y-%m") + '.log'

pathArchivo = sys.argv[1]
nombreArchivo = sys.argv[2]
tokenEmpresa = sys.argv[3]
conContable = sys.argv[4]

# Archivos y correos
log_path = '/fe/' + logfile
contab_path = '/fe/aut/' + nombreArchivo + '.TXT'
json_file_path = pathArchivo + nombreArchivo + '.jso'

# Verificar existencia del archivo JSON
try:
    with open(json_file_path, 'r') as json_data:
        d = json.load(json_data)
        JSONDocument = json.dumps(d, indent=4)  # Mejor formato para depuración
        logging.debug("Contenido del JSON cargado: %s", JSONDocument)
except IOError:
    logging.error("Error: No se encontró el archivo JSON en %s", json_file_path)
    sys.exit(1)
except ValueError as e:
    logging.error("Error al decodificar JSON: %s", str(e))
    sys.exit(1)

# Petición a la API con manejo de SSL
try:
    logging.debug("Enviando solicitud a la API...")
    try:
        r = requests.post(url, data={'JSONDocumento': JSONDocument}, headers={'token': tokenEmpresa}, verify=certifi.where())
    except requests.exceptions.SSLError:
        logging.warning("Fallo en la verificación SSL con certifi, intentando sin verificación...")
        r = requests.post(url, data={'JSONDocumento': JSONDocument}, headers={'token': tokenEmpresa}, verify=False)
    
    r.raise_for_status()
    respuestaServer = r.json()
    logging.debug("Respuesta de la API: %s", json.dumps(respuestaServer, indent=4))
except requests.exceptions.RequestException as e:
    logging.error("Error en la solicitud a la API: %s", str(e))
    sys.exit(1)

# Escritura de archivos de log y contabilidad
try:
    with open(contab_path, 'w') as contab, open(log_path, 'a+') as log:
        contab.write("%s %s %s %s\n\n" % (respuestaServer['claveAcceso'], conContable, respuestaServer['numDoc'], respuestaServer['tipoDoc']))
        log.write("%s %s %s OK\n" % (tiempoActual, nombreArchivo, conContable))
        logging.debug("Información escrita en los archivos correctamente.")
except IOError as e:
    logging.error("Error al escribir en archivos: %s", str(e))
    sys.exit(1)
