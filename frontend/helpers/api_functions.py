import requests
from requests.adapters import HTTPAdapter
import time
import threading
from typing import DefaultDict, Tuple, Callable, Union, Any, List
import os

class API_helper:
    """
    Clase de funciones extras que se usan dentro del frontend de la aplicación

    Args
        - (int) ID: id del usuario y/o la conversación
    """
    def __init__(self, id: int  = 1) -> None:
        """
        Iniciamos las URLs con los datos de la API y montamos la sesion (para poder meter el adaptador 
        y que no se reenvie la peticion sin querer y petemos el bot)
        """
        self.id = id

        self._session = requests.Session()

        self._ip = os.getenv("IWTJ_BIP", "127.0.0.1")
        self._port = os.getenv("IWTJ_BPORT", "5000")

        url = self._ip+":"+self._port

        self.API_URL = "http://"+url+"/peticion/"
        self.HEALTH_URL = "http://"+url+"/health"
        self.RAG_URL = "http://"+url+"/subirarchivo"

        #base de datos
        #self.URL_BASE = "http://127.0.0.1:5000"
        self.URL_BASE = "http://"+url
        self.login_extension = "/login"
        self.register_extension = "/register"
        self.get_array_extension = "/array_get"
        self.post_array_extension = "/array_post"

        self._headers = {}
        retries = 0
        self._adapter = HTTPAdapter(max_retries=retries)
        
        self._session.mount('http://', self._adapter)
        self._session.mount('http://', self._adapter)

    def set_id(self, id: str) -> None:
        """
        Updates the id of the helper so that it contains the user id

        Args:
            - (string) id: updated user id
        """
        self.id = id

    async def api_query(self, payload : DefaultDict, URL: str) -> DefaultDict:
        """
        Recibe el texto que se quiere pasar a la api y recibe la respuesta

        Args
            - (dictionary) payload: diccionario de parametros que queremos pasar a la API
            - (str) URL: url a la que se hace la peticion
        
        Returns
            - (dictionary) respuesta de la api
        """
        #response = requests.post(API_URL, headers=headers, json=payload)
        response = self._session.get(url=URL, headers=self._headers, params=payload)
        return response.json()
    
    async def query_question(self, payload : DefaultDict) -> str:
        """
        Expone la posibilidad de hacer la query de pedir una pregtuna

        Args
            - (dictionary) payload: diccionario de parametros que queremos pasar a la API
        
        Returns
            - (string) respuesta de la api
        """
        payload.update({"modo": "question"})
        datos = await self.api_query(payload, self.API_URL+str(self.id))
        return datos["respuesta"]
    
    async def query_example_response(self, payload : DefaultDict) -> str:
        """
        Expone la posibilidad de hacer la query de pedir una respuesta simulada
        a una pregunta

        Args
            - (dictionary) payload: diccionario de parametros que queremos pasar a la API
        
        Returns
            - (string) respuesta de la api
        """
        payload.update({"modo": "example"})
        datos = await self.api_query(payload, self.API_URL+str(self.id))
        return datos["respuesta"]
    
    async def query_for_grading(self, payload : DefaultDict) -> Tuple:
        """
        Expone la posibilidad de hacer la query de el grading de una pregunta

        Args
            - (dictionary) payload: diccionario de parametros que queremos pasar a la API
        
        Returns
            - (string, int) respuesta de la api
        """
        payload.update({"modo": "answer"})
        datos = await self.api_query(payload, self.API_URL+str(self.id))
        return datos["respuesta"], datos["array"]

    async def general_query(self, payload : DefaultDict) -> Tuple:
        """
        Q/A genérica

        Args
            - (dictionary) payload: diccionario de parametros que queremos pasar a la API
        
        Returns
            - (string) respuesta de la api
        """
        # sin modo
        datos = await self.api_query(payload, self.API_URL+str(self.id))
        return datos["respuesta"]

    async def rag_query(self) -> Tuple[str]:
        """
        Establece la comunicación con la api para poder realizar la subida de datos y devuelve
        los parametros del servidor ftp
        
        Returns
            - (list of strings) credenciales enviados por la API (addres, port, user, password)
        """
        response = self._session.get(self.RAG_URL)
        datos = response.json()

        return datos["address"], datos["port"], datos["user"], datos["password"]

    def start_health_checker(self, target: Callable) -> threading.Thread:
        """
        Funcion en la que podemos definir el comportamiento del servicio frente al estado de "salud"
        de la api. Recibe una función target que se ejecutará cada vez que cambie el estado de salud,
        se le pasará a target el estado de salud (tiene que tener en cuenta None: API caida)

        Args:
            - (function) target: funcion que se ejecutará -> target(health identifier (loading, healthy))
        
        Returns
            - (thread) el hilo que va a ejecutar la función target todo el rato (cada 2 s), hay que invocar .start()
        """
        def heatlh_checking_function():
            while True:
                health = None
                try:
                    response = self._session.get(self.HEALTH_URL)
                    health = response.json()["status"]
                except Exception:
                    health = None
                
                target(health)
                time.sleep(2)
                
        thread = threading.Thread(target=heatlh_checking_function)
        return thread
    
    async def login(self, user: str, password: str) -> Union[str, None]:
        """
        Intenta realizar el login con los credenciales, devuelve None si falla

        Args:
            - (string) user: username
            - (string) password

        Returns
            - (Union(str|None)) o la respuesta (id)(str) o None si falla
        """
        payload = {"user": user, "password": password}
        response = self._session.get(self.URL_BASE+self.login_extension, params=payload)
        try:
            return response.json()["id"] # fallo deberia ser NONE igual
        except Exception:
            return None
    
    async def register(self, user: str, password: str) -> Union[str, None]:
        """
        Intenta realizar un registro de usuario, devuelve None si falla (por ejemplo si usuario duplicado)

        Args:
            - (string) user: username
            - (string) password

        Returns
            - (Union(str|None)) o la respuesta (id)(str) o None si falla
        """        
        payload = {"user": user, "password": password}
        response = self._session.get(self.URL_BASE+self.register_extension, params=payload)
        try:
            return response.json()["id"] # fallo deberia ser NONE igual
        except Exception:
            return None
    
    async def get_array(self, id: str) -> List[Any]:
        """
        Intenta acceder al array de notas asociado a un usuario (por su id). Esta hardcodeado así
        que no debería fallar

        Args:
            - (string) id: id del usuario (tiene que ser el que devuelve login o register)
        
        Returns
            - (diccionario) la respuesta de la api
        """
        payload = {"id": id}
        try:
            response = self._session.get(self.URL_BASE+self.get_array_extension, params=payload)
            return response.json()["array"]
        except Exception:
            return [(0, 0.0),] # array de tuplas pq biene de con indice
    
    async def post_array(self, id: str, value: int) -> List[Any]:
        """
        FUNCION PARA PRUEBAS
        Intenta Actaulizar el array de notas asociado a un usuario (por su id). Esta hardcodeado así
        que no debería fallar. No se debería invocar ya que esto se debe manejar desde el backend.

        Args:
            - (string) id: id del usuario (tiene que ser el que devuelve login o register)
            - (int) value: la nota del usuario
        
        Returns
            - (diccionario) la respuesta de la api
        """
        payload = {"id": id, "value": value}
        try:
            response = self._session.get(self.URL_BASE+self.post_array_extension, params=payload)
            return response.json()["array"]
        except Exception:
            return [(0, 0.0),] # array de tuplas pq biene de con indice