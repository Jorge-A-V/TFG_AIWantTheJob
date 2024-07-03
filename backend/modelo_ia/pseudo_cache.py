from backend.modelo_ia.nemo_core import NemoCore

from typing import DefaultDict, Any

class Cache:
    """
    PseudoCache que precarga el contenido de una respuesta ejemplo antes de que el usuario lo pida.
    Funciona en base a la asumpción de que si el usuario quiere un ejemplo entonces habremos ahorrado 
    unos pocos segundos mientras que si el usuario quiere una corrección, entre que escribe la respuesta y 
    la envía la precarga ha terminado de sobra

    Args:
        - (NemoCore) nemo: instancia nemo que se encarga del procesamiento
    """
    def __init__(self, nemo: NemoCore = None) -> None:
        self.nemo = nemo
        self._cached_response = None

    async def get_content(self) -> DefaultDict[str, Any]:
        """
        Espera a que se complete la precarga y la devuelve

        Returns
            - (diccionario) con el contenido de la respuesta (formato de nemo normal)
        """
        response =  await self._cached_response
        self._cached_response = None
        return response
    
    def prepare_example(self, question: str) -> None:
        """
        Deja de manera asyncrona la respuesta precargandose

        Args:
            - (string) question: pregunta que se va a precargar
        """
        self._cached_response = None
        self._cached_response = self.nemo.processCall(question, "example")