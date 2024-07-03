import sys
sys.path.append("../")
import random

from backend.helpers.ftpserver import FTPserverEu #Eu de yo
from backend.helpers.parser import parser
from backend.modelo_ia.engine_proxy import Proxy
from backend.api.api import init
from backend.database.database import DataBase


def main():
    """
    Funcion de inicio
    """
    ftp_server = FTPserverEu() # declaración del ftpserver
    db = DataBase() # init de la base de datos

    # El parser tiene empaquetados token, model y cuantization
    proxy = Proxy(**parser(), database = db)

    # Le asignamos la función de on_load al ftp_server
    ftp_server.load(target=proxy.nemo_system.update_db)
    ftp_server.start() # inicializamos el ftp_server

    # inicializamos la api de flask con el proxy y el ftp_server definidos
    init(proxy=proxy, ftp_server_arg=ftp_server).run(debug=False)

if __name__ == "__main__":
    main()