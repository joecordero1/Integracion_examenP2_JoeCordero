from flask import Flask, request, jsonify
import jwt
from datetime import datetime
import requests

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

# Servicio SOAP externo
from zeep import Client

def llamar_servicio_soap(datos):
    print(f"Llamando al servicio SOAP")
    tipo = datos.get("tipo")
    wsdl_url = "http://localhost:8002/?wsdl"
    client = Client(wsdl=wsdl_url)
    return client.service.procesarSolicitud(tipo)


# POST /solicitudes
@app.route("/solicitudes", methods=["POST"])
def crear_solicitud():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token JWT requerido"}), 401

    token = auth_header.split(" ")[1]
    valido, usuario = verificar_token(token)
    if not valido:
        return jsonify({"error": "Token inválido"}), 403

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

    solicitudes[solicitud_id] = solicitud
    return jsonify(solicitud), 201

# GET /solicitudes/<id>
@app.route("/solicitudes/<solicitud_id>", methods=["GET"])
def obtener_solicitud(solicitud_id):
    solicitud = solicitudes.get(solicitud_id)
    if not solicitud:
        return jsonify({"error": "Solicitud no encontrada"}), 404
    return jsonify(solicitud)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
