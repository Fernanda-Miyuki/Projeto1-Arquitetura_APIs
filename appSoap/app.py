from flask import Flask, jsonify
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from controllers.animal_controller import AnimalSOAPController

spyne_app = Application(
    services=[AnimalSOAPController],
    tns='http://meuzoo.com/schemas/animal',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

soap_wsgi_app = WsgiApplication(spyne_app)

flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return jsonify({
        "status": "ON",
        "servico": "API SOAP de Cadastro de Animais",
        "wsdl": "http://localhost:5000/soap?wsdl"
    })

app_composta = DispatcherMiddleware(
    flask_app.wsgi_app,
    {
        '/soap': soap_wsgi_app  # type: ignore
    }
)

if __name__ == '__main__':
    print("Servidor rodando em http://localhost:5000")
    print("Acesse o WSDL em: http://localhost:5000/soap?wsdl")
    run_simple('localhost', 5000, app_composta, threaded=True)