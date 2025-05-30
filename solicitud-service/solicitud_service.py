from flask import Flask, request, jsonify
import jwt
from datetime import datetime
import requests
import logging

from zeep import Client
from tenacity import retry, stop_after_attempt, wait_fixed
import pybreaker

# Configurar logging (a archivo y consola)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("solicitud_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
SECRET_KEY = "clave_secreta_para_validar"

# Simulación de base de datos en memoria
solicitudes = {}

# Verificación de JWT
def verificar_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True, decoded
    except jwt.InvalidTokenError:
        return False, None

# Circuit Breaker config
breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30
)

# Retry + Circuit Breaker para el SOAP
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
@breaker
def llamar_servicio_soap(datos):
    tipo = datos.get("tipo")
    wsdl_url = "http://localhost:8002/?wsdl"
    try:
        logger.info(f"Llamando al servicio SOAP con tipo: {tipo}")
        client = Client(wsdl=wsdl_url)
        respuesta = client.service.procesarSolicitud(tipo)
        logger.info(f"Respuesta del SOAP: {respuesta}")
        return respuesta
    except Exception as e:
        logger.error(f"Error llamando al servicio SOAP: {str(e)}")
        raise

# POST /solicitudes
@app.route("/solicitudes", methods=["POST"])
def crear_solicitud():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Token JWT ausente o mal formado")
        return jsonify({"error": "Token JWT requerido"}), 401

    token = auth_header.split(" ")[1]
    valido, usuario = verificar_token(token)
    if not valido:
        logger.warning("Token JWT inválido")
        return jsonify({"error": "Token JWT inválido"}), 403

    datos = request.get_json()
    solicitud_id = str(len(solicitudes) + 1)
    estado = llamar_servicio_soap(datos)

    solicitud = {
        "id": solicitud_id,
        "usuario": usuario["user"],
        "estado": estado,
        "fecha": datetime.utcnow().isoformat(),
        "datos": datos
    }
    logger.info(f"Creando solicitud para usuario: {usuario['user']}")

    solicitudes[solicitud_id] = solicitud
    return jsonify(solicitud), 201

# GET /solicitudes/<id>
@app.route("/solicitudes/<solicitud_id>", methods=["GET"])
def obtener_solicitud(solicitud_id):
    solicitud = solicitudes.get(solicitud_id)
    if not solicitud:
        logger.warning(f"Solicitud {solicitud_id} no encontrada")
        return jsonify({"error": "Solicitud no encontrada"}), 404
    return jsonify(solicitud)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
