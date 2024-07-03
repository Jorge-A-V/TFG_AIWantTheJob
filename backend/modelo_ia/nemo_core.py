from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers import(
    register_llm_provider
)
from langchain.chains import RetrievalQA
from typing import Callable, List, DefaultDict, Tuple, Any, Union

from backend.modelo_ia.vector_store import VectoreStore
from backend.modelo_ia.nemo_config import NemoConfig
from backend.modelo_ia.generic_llm import LLM
import os
from os import walk


class NemoCore:
    """
    Clase interna que encapsula el nemo engine. Instancia los railes de comportamiento.

    Args:
        - (VectoreStore) db: instancia de la base de datos vectorial (iniciada no cargada)
        - (NemoConfig) nemo_config: instancia de las configuraciones de Nemo
        - (LLM) instancia del modelo interno que se va a emplear en el engine
    """
    def __init__(self, db: VectoreStore = None, nemo_config: NemoConfig = None, llm: LLM = None) -> None:        
        self.nemo_config = nemo_config
        self.LLM = llm

        self.db = db
        self.has_rag = None

        self.rails = None
        self._start_engine()

    """
    ---------------------------------------------------------------------------
    FUCIONES DE SETUP DEL NEMO ENGINE
    ---------------------------------------------------------------------------
    """

    def _start_engine(self):
        """
        Funcion privada que inicializa los railes de Nemo a partir de las configuraciones.

        Insider Args:
            - (string) YAML_CONFIG: configuración del motor de nemo
            - (string) COLANG_CONFIG: configuración del flow de conversación de nemo            
        """
        
        if self.LLM is None:
            self.LLM = LLM() #default args

        HFPipeline = get_llm_instance_wrapper(
            llm_instance=self.LLM.llm, llm_type=self.nemo_config.engine
        )
        register_llm_provider(self.nemo_config.engine, HFPipeline)

        config = RailsConfig.from_content(self.nemo_config.COLANG_CONFIG, self.nemo_config.YAML_CONFIG)
        rails = LLMRails(config)
        
        #rails.register_action(action=self.question_response, name="response")
        #rails.register_action(action=self.punctuate_answer, name = "user_answer")
        #rails.register_action(action=self.emulate_answer, name = "bot_answer")

        self.rails = rails

        self.register_actions(
            [self.LLM.question_response, self.LLM.punctuate_answer, self.LLM.emulate_answer],
            ["bot_response", "user_answer", "bot_answer"],
            [True, False, False]
        )
        """
        # Para el naive
        self.register_actions(
            [self.LLM.question_response, self.LLM.punctuate_answer, self.LLM.emulate_answer, self.LLM.summarize],
            ["bot_response", "user_answer", "bot_answer", "summarize"],
            [True, False, False, False]
        )
        """

        try:
            # cwd is scripts by default
            f = []
            for (_, _, filenames) in walk("../backend/archivos/base"):
                f.extend(filenames)
                break
            for file in f:
                try:
                    print("intentando", file)
                    self.db.load_and_embed(f"../backend/archivos/base/{file}", "general_context", 800, 200)
                except Exception as e:
                    raise e
                    print("error")
                    pass
        except Exception as e:
            raise e
            pass

    def register_actions(self, callbacks: List[Callable], names: List[str], similarity_questions: list[bool]) -> None:
        """
        Funcion que registra una lista de acciones en el engine de nemo

        Args:
            - (lista de funciones) callbacks: lista de callbacks
            - (lista de strings) names: nombre de los callbacks dentro del .co del config
            - (lista de bool) similarity_questions: do search for similarity search for questions
        """
        for i, (action, name) in enumerate(zip(callbacks, names)):
            self.register_action(action, name, question=similarity_questions[i])

    def register_action(self, callback: Callable, name: str, question: bool = False) -> None:
        """
        Funcion que registra una una accion en el engine de nemo

        Args:
            - (funcion) callback: funcion a llamar
            - (string) names: nombre de dicha funcion dentro del .co del config
            - (bool) question: do search for similarity search for questions
        """
        def callback_with_context(inputs: str):
            inputs = self._set_context(inputs, question)
            print(inputs)
            return callback(inputs)

        self.rails.register_action(action=callback_with_context, name=name)

    def _set_context(self, text: str, question: bool = False) -> str:
        """
        Añade a una query existente el contexto de manera manual

        Args:
            - (string) text: texto para buscar el contexto
            - (bool) question: habilita la busqeda por similitud de las preguntas

        Returns
            - (string) nueva query con el contexto añadido
        """
        global_context, client_context, other_context = self._get_context(text, question)

        if global_context is not None:
            text += f"\nSome general context you may use is: {global_context}"
        if client_context is not None:
            text += f"\The specific context is: {client_context}"
        if other_context is not None:
            text += f"\nSome similar examples found are: {other_context}"
        
        return text

    def _get_context(self, text: str, question: bool = False) -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
        """
        Devuelve el contexto en la base de datos vectorial

        Args:
            - (string) text: texto para buscar el contexto
            - (bool) question: habilita la busqeda por similitud de las preguntas

        Returns
            - (tuple) global context + client context + other context, todas pueden ser None
        """
        return self.db.get_context(text, question)
    
    """
    ---------------------------------------------------------------------------
    FUCIONES QUE EXPONE EL PROCESAMIENTO DELLAMADAS
    ---------------------------------------------------------------------------
    """

    def _get_complete_args(self, mode: str = None) -> DefaultDict[str, str]:
        """
        Funcion que sirve para poner los argumentos correspondientes al flujo de nemo

        Args:
            - (string) mode: modo recibido

        Returns 
            - (DefaultDict) diccionario tipo "context" para nemo
        """
        args = {}
        if mode == "question":
            args = {"question": True, "answer": False, "example": False}
        if mode == "answer":
            args = {"question": False, "answer": True, "example": False}
        if mode == "example":
            args = {"question": False, "answer": False, "example": True}
        complete_args = {
                "role": "context", "content": args
        }
        return complete_args

    async def processCall(self, text: str, args: str = None) -> str:
        """
        Funcion que procesa la llamada en el modelo.

        Args:
            - (string) text: texto que equivale a la query que se pasa como user input
            al sistema nemo+IA
            - (string) args: modo de la pregunta
        
        Returns:
            - El contenido que la IA genere
        """
        try:
            messages = [
                self._get_complete_args(args), 
                {"role": "user", "content": text}
            ]
            res = await self.rails.generate_async(messages=messages)
            print("Res:", res)
            return res
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
            return "algo ha fallado"
        
    """
    ---------------------------------------------------------------------------
    FUCIONES DE TRATAMIENTO CON EL RAG, VS
    ---------------------------------------------------------------------------
    """

    def update_db(self, document_path: str, remove: bool = True) -> None:
        """
        Función que actualiza el estado interno del sistema, cargando los documentos para poder hacer rag
        y esblaciendo el estado actual a rag: si

        Args:
            - (string) document_path: path del archivo que se quiere leer
            - (bool) remove: indica si se va a eliminar el documento
        """
        
        self.db.load_and_embed(document_path) #this is the client_side
        
        if remove:
            os.remove(document_path)
