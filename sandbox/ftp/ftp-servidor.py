
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
app = Flask(__name__)

CORS(app)

#https://pyftpdlib.readthedocs.io/en/latest/api.html
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
usuario = "generic"
password = "1234"
direccion = "localhost"
puerto = 9999

authorizer.add_user(usuario, password, "./archivos", perm="w")
handler = FTPHandler
handler.authorizer = authorizer
handler.banner = "Conexion disponible para ser iniciada"
address = ('127.0.0.1', puerto)

def iniciarServidorFTP():
    server = FTPServer(address, handler)
    server.serve_forever()

@app.route("/subirarchivo")
def peticion():
    datos_ftp = {  
        "user": usuario,
        "password": password,
        "address": direccion,
        "port": puerto,
    }
    return jsonify(datos_ftp), 200 


if __name__ == "__main__":
    threading.Thread(target=iniciarServidorFTP).start()
    app.run(host="127.0.0.1", port = 9998, debug=True)