from huggingface_hub import login

from backend.modelo_ia.vector_store import VectoreStore
from backend.modelo_ia.nemo_core import NemoCore
from backend.modelo_ia.nemo_config import NemoConfig
from backend.helpers.number_graber import NumberGrabber
from backend.modelo_ia.generic_llm import LLM
from backend.modelo_ia.pseudo_cache import Cache
from backend.database.database import DataBase

from typing import Literal, List, Any, DefaultDict, Union
import time
class Proxy:
    """
    Clase proxy para relacionarse con el sistema
    
    Args:
        - (string) token: token para loggearse en huggingface, para poder acceder a repositorios y modelos semi-privados
        como el llama
        - (string) model_name: nombre del modelo que vamos a utilizar
        - (literal) cuatization: indicador de la cuatización del modelo
        - (Database) database of things to process
    """
    def __init__(self, token: str = None, model_name: str = None, cuantization: Literal["4bit","8bit"] = "4bit", database: DataBase = None) -> None:
        
        self.database = database

        if token:
            login(token)

        VS = VectoreStore()
        config = NemoConfig(model_name)
                

        self.llm = LLM(model_name=model_name, loading_mode=cuantization)#LLM(model_name=model_name, loading_mode=cuantization)

        self.nemo_system = NemoCore(
            VS, config, self.llm
        )

        self.cache = Cache(self.nemo_system)

    def update_to_client_rag(self, document_path: str, remove: bool = True) -> None:
        """
        Funcion que actualiza el sistema. Cargando el contenido dell documento y estableciendo el modo rag:si

        Args:
            - (string) document_path: path hasta el documento que hay que leer
            - (bool) remove: indica si se borra el fichero o no
        """
        self.nemo_system.update_db(document_path, remove)

    async def get_data(self, text: str, args: str, id: str) -> str:
        """
        Funcion que hace una llamada al sistema (query)

        Args
            - (string) text: texto que se equivale a la query al modelo
            - (args) posibles argumentos de entrada

        Returns
            - (string) la respuesta del modelo
        """
        response_dict = {}

        if args == "example":
            res = await self.cache.get_content() #ya se estaba pre-cargando la respuesta
        else:
            print("1")
            try:
                _ = await self.cache.get_content() # si esta precargando tenemos que esperar (no debería pasar nunca)
            except Exception:
                pass
            res = await self.nemo_system.processCall(text=text, args=args)
            print("2")

        response = res["content"]
        if args == "question":
            self.nemo_system.db.add_question(context=text, question=response)
            print("3")
            self.cache.prepare_example(response) #async asi que deberia ser capaz de volver
            print("4")
            

        if args == "answer":
            nota = NumberGrabber().grab_number(response)
            response_dict = self.insertar_valor_array(id, nota)

        response_dict.update({"respuesta": response})
        return response_dict

    """
    ---------------------------------------------------------------------------
    DATABASE PROXY
    ---------------------------------------------------------------------------
    """

    def registrar_usuario(self, nombre: str, password: str) -> Union[DefaultDict[str, Any], None]:
        """
        Accede a la base de datos y registra a un usuario:

        Args:
            - (string) nombre: nombre del usuario
            - (string) password: contraseña

        Returns
            - (diccionario o None) el id en usuario o None
        """
        id = self.database.registrar_usuario(nombre, password)
        if id == "Name probably registered or internal error":
            return None
        return {"id": id}
    
    def validar_usuario(self, nombre: str, password: str) -> Union[DefaultDict[str, Any], None]:
        """
        Realiza la validación del usuario (es decir si existe en la bd)

        Args:
            - (string) nombre: nombre del usuario
            - (string) password: contraseña

        Returns
            - (diccionario o None) el id en usuario o None
        """
        id = self.database.validar_usuario(nombre, password)
        if id == "Error on validation":
            return None
        return {"id": id}
        
    def insertar_valor_array(self, identifier: str, value: int) -> DefaultDict[str, Any]:
        """
        Accede a la base de datos e inserta un valor en el array de datos del usuario

        Args:
            - (string) identifier: hash id del usuario
            - (int) value: valor a insertar

        Returns
            - (diccionario) que contiene el array de datos ["array"]
        """
        array = self.database.insertar_valor_array(identifier, value)
        return {"array": array}
        
    def recuperar_valores_array(self, identifier: str) -> DefaultDict[str, Any]:
        """
        Accede a la base de datos y obtiene el array de valores de un usuario

        Args:
            - (string) identifier: hash id del usuario

        Returns
            - (diccionario) que contiene el array de datos ["array"]
        """
        array = self.database.recuperar_valores_array(identifier)
        return {"array": array}
