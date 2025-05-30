from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

class CertificadoService(ServiceBase):

    @rpc(Unicode, _returns=Unicode)
    def procesarSolicitud(ctx, tipo):
        if tipo == "certificado":
            return "procesado"
        elif tipo == "homologacion":
            return "en revisión"
        else:
            return "rechazado"

app = Application([CertificadoService],
                  tns='http://servicios.certificados.utm.edu.ec/',
                  in_protocol=Soap11(),
                  out_protocol=Soap11())

wsgi_app = WsgiApplication(app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print("SOAP service corriendo en http://localhost:8002")
    server = make_server('0.0.0.0', 8002, wsgi_app)
    server.serve_forever()
