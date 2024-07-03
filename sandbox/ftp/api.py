from modulosExtra import parser
import sys
sys.path.append("../modelo_ia")

from basicModel import startRunning, processCall

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

llm = None


@app.route("/prueba")
def prueba():
    datos = {
        "id": 12,
        "respuesta": "hooooolllllaaa"
    }
    return jsonify(datos), 200

@app.route("/peticion/<id>")
def peticion(id):

    datos = {
        "id": id,
    }
    print(request)
    pregunta = request.args.get("pregunta")
    print(f"peticion recibida: {pregunta}")
    if pregunta:
        datos["pregunta"] = pregunta
        print("procesando datos")
        datos["respuesta"] = processCall(llm, pregunta)
    else:
        datos["respuesta"] = "pregunta vacia"
    print(f"datos procesados {datos}")
    return jsonify(datos), 200 #devolvemos los datos en json y status OK


if __name__ == "__main__":
    llm = startRunning(parser())
    app.run(debug=True)