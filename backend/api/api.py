import sys
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.helpers.ftpserver import FTPserverEu #Eu de yo
from backend.modelo_ia.engine_proxy import Proxy

#creamos la entidad app y le damos permisos CORS
app = Flask(__name__)
CORS(app)

#variable que indica la salud del modelo
global status
status = 1

system_proxy = None
ftp_server = None

"""
-----------------------------------------------------------------
FUCIONES DE USO
-----------------------------------------------------------------
"""

@app.route("/health")
def get_health():
    """
    Funcion de health típica de un servidor
    """
    print(status)
    if status == 1:
        return jsonify({"status": "available"}), 200
    else:
        return jsonify({"status": "loading"}), 200

@app.route("/subirarchivo")
def subirarchivo():
    """
    Devuelve un diccionario de datos con los valores para conectarse al ftpserver
    """
    datos_ftp = ftp_server.get_data_as_dic()
    return jsonify(datos_ftp), 200 



@app.route("/peticion/<id>")
async def peticion(id): # <- específica
    """
    Devuelve la respuesta a la query que se le pasa, hace uso de proxy
    """

    datos = {
        "id": id,
    }

    print(request)

    # cogemos los argumentos para el proxy
    pregunta = request.args.get("pregunta")
    modo = request.args.get("modo")

    print(f"peticion recibida: {pregunta}")

    if pregunta:
        datos["pregunta"] = pregunta
        response = await system_proxy.get_data(pregunta, args=modo, id=id)
        datos.update(response)
    else:
        datos["respuesta"] = "pregunta vacia"

    print(f"datos procesados {datos}")
    return jsonify(datos), 200 #devolvemos los datos en json y status OK  
"""
#Genérica
async def peticion(id):
    datos = {
        "id": id,
    }
    pregunta = request.args.get("pregunta")
    if pregunta:
        datos["pregunta"] = pregunta
        response = await system_proxy.get_data(pregunta, args=None, id=id)
        datos.update(response)
    else:
        datos["respuesta"] = "pregunta vacia"
    return jsonify(datos), 200 #devolvemos los datos en json y status OK  
"""



@app.route("/login")
async def login():
    """
    Función para hacer login en la base de datos
    """
    # Cogemos credenciales y usamos el proxy para conectarnos a la db
    user, password = request.args.get("user"), request.args.get("password")
    response = system_proxy.validar_usuario(user, password)
    if response == None:
        return {"id": None}, 200
    else:
        return jsonify(response), 200

@app.route("/register")
async def register():
    """
    Función para hacer register en la base de datos
    """
    # Cogemos credenciales y usamos el proxy para conectarnos a la db
    user, password = request.args.get("user"), request.args.get("password")
    response = system_proxy.registrar_usuario(user, password)
    if response == None:
        return {"id": None}, 200
    else:
        return jsonify(response), 200
    
@app.route("/array_post")
async def array_post():
    """
    Función para subir datos de un archivo
    """
    # Cogemos el id y el valor
    id, value = request.args.get("id"), request.args.get("value")
    response = system_proxy.insertar_valor_array(id, value)
    return jsonify(response), 200

@app.route("/array_get")
async def array_get():
    """
    Función coger los valores de un array
    """
    # Cogemos el id y el valor
    id = request.args.get("id")
    response = system_proxy.recuperar_valores_array(id)
    return jsonify(response), 200

"""
-----------------------------------------------------------------
FUCIONES DEPRUEBA
-----------------------------------------------------------------
"""

@app.route("/prueba_corta")
def prueba_corta():
    """
    Función de prueba, respuesta instantanea
    """
    datos = {
        "id": 1,
        "respuesta": "prueba_corta"
    }
    return jsonify(datos), 200

@app.route("/prueba_larga")
def prueba_larga():
    """
    Función de prueba, respuesta después de 5 secs
    """
    datos = {
        "id": 1,
        "respuesta": "prueba_corta"
    }
    time.sleep(5)
    return jsonify(datos), 200

"""
-----------------------------------------------------------------
FUCION DE INICIO DE LA API
-----------------------------------------------------------------
"""

def init(proxy: Proxy, ftp_server_arg: FTPserverEu):
    global system_proxy
    system_proxy = proxy
    global ftp_server
    ftp_server = ftp_server_arg
    return app
    
"""from modulosExtra import parser
import sys
import threading

sys.path.append("../modelo_ia")

import model_class

from flask import Flask, request, jsonify
from flask_cors import CORS

#https://pyftpdlib.readthedocs.io/en/latest/api.html
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
usuario = "generic"
password = "1234"
direccion = "localhost"
puerto = 9999

class MyHandler(FTPHandler):
    def on_file_received(self, file):
        llm.update_to_rag(file)
        return super().on_file_received(file)

authorizer.add_user(usuario, password, "./archivos", perm="w")

def iniciarServidorFTP():
    handler = MyHandler
    handler.authorizer = authorizer
    handler.banner = "Conexion disponible para ser iniciada"
    address = ('127.0.0.1', puerto)
    server = FTPServer(address, handler)
    server.serve_forever()

global llm
llm = None       

app = Flask(__name__)

CORS(app)

global status
status = 1

@app.route("/health")
def get_health():
    print(status)
    if status == 1:
        return jsonify({"status": "available"}), 200
    else:
        return jsonify({"status": "loading"}), 200

@app.route("/subirarchivo")
def subirarchivo():
    datos_ftp = {  
        "user": usuario,
        "password": password,
        "address": direccion,
        "port": puerto,
    }
    return jsonify(datos_ftp), 200 

@app.route("/prueba")
def prueba():
    datos = {
        "id": 12,
        "respuesta": "hooooolllllaaa"
    }
    return jsonify(datos), 200

@app.route("/peticion/<id>")
async def peticion(id):

    datos = {
        "id": id,
    }
    print(request)
    pregunta = request.args.get("pregunta")
    print(f"peticion recibida: {pregunta}")
    if pregunta:
        datos["pregunta"] = pregunta
        print("procesando datos")
        datos["respuesta"] = await llm.get_data(pregunta, None)
    else:
        datos["respuesta"] = "pregunta vacia"
    print(f"datos procesados {datos}")
    return jsonify(datos), 200 #devolvemos los datos en json y status OK  

@app.route("/question/<id>")
async def question(id):

    datos = {
        "id": id,
    }
    print(request)
    pregunta = request.args.get("pregunta")
    print(f"peticion recibida: {pregunta}")
    if pregunta:
        datos["pregunta"] = pregunta
        print("procesando datos")
        datos["respuesta"] = await llm.get_data(pregunta, "question")
    else:
        datos["respuesta"] = "pregunta vacia"
    print(f"datos procesados {datos}")
    return jsonify(datos), 200 #devolvemos los datos en json y status OK  

@app.route("/answer/<id>")
async def answer(id):

    datos = {
        "id": id,
    }
    print(request)
    pregunta = request.args.get("pregunta")
    print(f"peticion recibida: {pregunta}")
    if pregunta:
        datos["pregunta"] = pregunta
        print("procesando datos")
        datos["respuesta"] = await llm.get_data(pregunta, "answer")
    else:
        datos["respuesta"] = "pregunta vacia"
    print(f"datos procesados {datos}")
    return jsonify(datos), 200 #devolvemos los datos en json y status OK  

@app.route("/example/<id>")
async def example(id):

    datos = {
        "id": id,
    }
    print(request)
    pregunta = request.args.get("pregunta")
    print(f"peticion recibida: {pregunta}")
    if pregunta:
        datos["pregunta"] = pregunta
        print("procesando datos")
        datos["respuesta"] = await llm.get_data(pregunta, "example")
    else:
        datos["respuesta"] = "pregunta vacia"
    print(f"datos procesados {datos}")
    return jsonify(datos), 200 #devolvemos los datos en json y status OK  

if __name__ == "__main__":
    llm = model_class.LLM_interface(parser())
    threading.Thread(target=iniciarServidorFTP).start()
    app.run(debug=False)
"""