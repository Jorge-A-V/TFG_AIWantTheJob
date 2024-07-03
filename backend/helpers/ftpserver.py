from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import threading
from typing import Callable, DefaultDict

class FTPserverEu:
    """
    Clase servidor ftp. Abstrae toda la lógica de la conexión ftp.
    """

    def __init__(self):
        """
        Función de iniciio. Establece los parametros base del servidor (dirección, usuario, puerto, contraseña) y 
        el autorizador
        """
        self._authorizer = DummyAuthorizer()
        self._usuario = "generic"
        self._password = "1234"
        self._direccion = "localhost"
        self._puerto = 9999

        self._authorizer.add_user(self._usuario, self._password, "./archivos", perm="w")

        self.server = None

    def get_data_as_dic(self) -> DefaultDict[str, str]:
        """
        Funcion que devuelve usuario, contraseña, dirección y puerto como un diccionario

        Returns
            - (dic) contiene usuario, contraseña, dirección y puerto
        """
        return {  
            "user": self._usuario,
            "password": self._password,
            "address": self._direccion,
            "port": self._puerto,
        }

    def load(self, target: Callable) -> None:
        """
        Función para "cargar" el servidor. Recibe una función target que se ejecuta sobre el fichero cuando se recibe

        Args
            - (funcion) target: funcion que se ejecuta sobre el fichero on_recive (tiene como params el propio fichero
            [taget(file)])
        """
        class MyHandler(FTPHandler): #creamos el handler custom para tratar el fichero on_receive
            def on_file_received(self, file):
                target(file)
                return super().on_file_received(file)
        
        handler = MyHandler
        handler.authorizer = self._authorizer
        handler.banner = "Conexion disponible para ser iniciada"
        address = (self._direccion, self._puerto)
        self.server = FTPServer(address, handler) #Creamos la case servidor con la dirección y el handler definidos previamente

    def _start(self):
        """
        Función privada, realiza el serve_forever() del servidor
        """
        self.server.serve_forever()

    def start(self) -> threading.Thread:    
        """
        Función para iniciar el servidor ftp en un hilo diferente.

        Returns
            - (Thread) identificador del thread en el que se está ejecutando el servidor
        """
        t = threading.Thread(target=self._start).start()
        return t