# Plataforma de Servicios Estudiantiles 🎓

Este proyecto implementa una arquitectura moderna basada en microservicios, que expone servicios REST y SOAP para la gestión de solicitudes de certificados y homologaciones académicas. Se incluye autenticación JWT, API Gateway con Kong, Circuit Breaking, Retry y capacidades de trazabilidad y monitoreo.

---

## 🧱 Componentes de la Arquitectura

- **Cliente**: Solicita certificados mediante `/solicitudes`.
- **API Gateway (Kong)**: Aplica seguridad (API Key), rate limiting, y enruta solicitudes.
- **SolicitudService (REST)**:
  - Verifica JWT.
  - Llama a un servicio SOAP.
  - Guarda solicitudes en memoria.
- **Sistema Académico (REST interno)**: Consultas futuras (simulado).
- **Servicio SOAP (Spyne)**: Procesa certificados u homologaciones.
- **Sistema de Seguridad (JWT)**: Genera tokens.
- **Trazabilidad**: Logs detallados.
- **Monitoreo (sugerido)**: Jaeger, Prometheus, Grafana.

---

## 🚀 Configuración de Kong Gateway

### Crear red
```bash
docker network create kong-net
```

### Base de datos de Kong
```bash
docker run -d --name kong-database --network=kong-net -p 5433:5432 \
  -e POSTGRES_USER=kong \
  -e POSTGRES_DB=kong \
  -e POSTGRES_PASSWORD=kong \
  postgres:13
```

### Migrar base de datos
```bash
docker run --rm --network=kong-net \
  -e KONG_DATABASE=postgres \
  -e KONG_PG_HOST=kong-database \
  -e KONG_PG_USER=kong \
  -e KONG_PG_PASSWORD=kong \
  kong:3.6 kong migrations bootstrap
```

### Levantar Kong
```bash
docker run -d --name kong --network=kong-net \
  -p 8000:8000 -p 8001:8001 \
  -e KONG_DATABASE=postgres \
  -e KONG_PG_HOST=kong-database \
  -e KONG_PG_USER=kong \
  -e KONG_PG_PASSWORD=kong \
  -e KONG_ADMIN_LISTEN=0.0.0.0:8001 \
  kong:3.6
```

---

## 🔐 Seguridad en Gateway

```bash
# Registrar servicio
curl -i -X POST http://localhost:8001/services/ \
  --data "name=solicitud-service" \
  --data "url=http://host.docker.internal:8081"

# Crear ruta
curl -i -X POST http://localhost:8001/services/solicitud-service/routes \
  --data "paths[]=/api/solicitudes"

# Habilitar API Key
curl -i -X POST http://localhost:8001/services/solicitud-service/plugins \
  --data "name=key-auth"

# Crear consumidor
curl -i -X POST http://localhost:8001/consumers/ \
  --data "username=estudiante_token"

# Asignar API Key
curl -i -X POST http://localhost:8001/consumers/estudiante_token/key-auth
```

---

## 🔁 Circuit Breaking & Retry

Se utiliza `pybreaker` y `tenacity`:

```python
breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

@retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
@breaker
def llamar_servicio_soap(datos):
    ...
```

---

## 📊 Monitoreo y Trazabilidad

- **Logs**: Se escriben en consola y archivo `solicitud_service.log`.
- **Herramientas sugeridas**:
  - Jaeger: Trazabilidad distribuida.
  - Prometheus + Grafana: Métricas de performance.
  - Elastic Stack: Análisis de logs.

---

## ▶️ Ejecutar el proyecto

```bash
pip install -r requirements.txt
python app.py
```

---

## 📦 Dependencias

- Flask
- PyJWT
- Spyne
- Zeep
- Tenacity
- PyBreaker

---

## 👨‍💻 Autor

Joe Cordero  
Universidad Técnica de Manabí  
Integración de Sistemas - Progreso 2  
2025
