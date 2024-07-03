import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import PDFMinerLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from torch import cuda
from typing import Union, Tuple
import regex
import uuid

class VectoreStore:
    """
    Clase base de datos vectorial dinámica. Se usa para instanciar una vectorestore
    con un documento para poder realizar RAG sobre dicho docuemnto

    Args
        - (string) embd_modelname: nombre del modelo para realizar los embeddings al guardarlo
        en la vectorial db. Tiene que funcionar con langchain HuggingFaceEmbeddings
    """
    def __init__(self, embd_modelname: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        """
        Funcion de inicio, se inicia el cliente y el modelo de embedding
        """
        self.client = chromadb.PersistentClient(path="../backend/database/data")
        self.embedding_model = self._start_embd_model(embd_modelname)
        self.db = None

        self.client.get_or_create_collection(
            name = "similarity_context",
            metadata = {"hnsw:space": "cosine"} # Usamos cosenos para similaridad
        )

        try:
            # Borramos la colección si existe (no deberia ser permanente)
            self.client.delete_collection("general_context")
        except Exception:
            pass
    
        try:
            # Borramos la colección si existe (no deberia ser permanente)
            self.client.delete_collection("client_context")
        except Exception:
            pass

        # las iniciamos
        self.client.get_or_create_collection(
            name = "client_context",
            metadata = {"hnsw:space": "cosine"} # Usamos cosenos para similaridad
        )
        self.client.get_or_create_collection(
            name = "general_context",
            metadata = {"hnsw:space": "cosine"} # Usamos cosenos para similaridad
        )

    def _start_embd_model(self, embd_modelname: str) -> HuggingFaceEmbeddings:
        """
        Funcion privada que inicializa el modelo de embeddings. Se mira si se peude usar cpu o cuda y  se
        establece el batch_size a 32

        Args
            - (string) embd_modelname: nombre del modelo para realizar los embeddings al guardarlo
            en la vectorial db. Tiene que funcionar con langchain HuggingFaceEmbeddings

        Returns
            - (HuggingFaceEmbeddings) modelo de embeddings instanciado
        """
        device = "cpu"
        # si tienes suficiente VRAM f"cuda:{cuda.current_device()}" if cuda.is_available() else "cpu"

        embedding_model = HuggingFaceEmbeddings(
            model_name = embd_modelname,
            model_kwargs = {"device": device},
            encode_kwargs = {"device": device, "batch_size": 8} # lento pero no consume muchos recursos
        )

        return embedding_model
    
    def load_and_embed(self, document_route: str, index_name:str = "client_context", chunk_size = 600, chunk_overlap = 200) -> None:
        """
        Funcion para cargar el documento en la base de datos.

        Args:
            - (string) document_route: path al documento que se quiere leer (de momento solo pdf)
            - (string) index_name: nombre de la colecicón en la DB
            - (int) chunk_size: tamaño de los splits del documento
            - (int) chunk_overlap: tamaño de la cantidad de texto compatido entre elementos  a:c - c:b (c compartido)
        """
        collection = self.client.get_or_create_collection( # para las 3 prinipales debería existir ya
            name = index_name,
            metadata = {"hnsw:space": "cosine"} # Usamos cosenos para similaridad
        )

        # Leemos el pdf y usamos un splitter para dividirlo en minidocumentos
        loader = PDFMinerLoader(document_route)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True
        )
        doc_splitted = splitter.split_documents(docs)  
        
        # embebemos los documentos y los guardamos en la colección
        embeddings = self.embedding_model.embed_documents([doc.page_content for doc in doc_splitted])

        collection.add(
            ids = [str(uuid.uuid4())+str(i) for i in range(len(doc_splitted))],
            documents=[doc.page_content for doc in doc_splitted], embeddings=embeddings
            )
    
    def get_context(self, text: str, question: bool = False) -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
        """
        Devuelve el contexto que se tiene en la base de datos (en todas las colecciones)

        Args:
            - (string) text: texto base para el RAG
            - (bool) question: habilita si buscar preguntas similares o no

        Returns
            - (tuple) global context + client context + other context, cualquiera puede ser None
        """
        
        #General context
        general_context = self._get_document(text, "general_context")

        #Client Context
        client_context = self._get_document(text, "client_context")

        #Similarity Context
        if question:
            similarity_context = self._get_question(text, "similarity_context")
        else:
            similarity_context = False

        return general_context, client_context, similarity_context

    def _get_document(self, text: str, index_name: str) -> Union[str, None]:
        """
        Devuelve el contexto (documento) que se recupere de la colección <index_name>

        Args
            - (string) text: texto a buscar similaridades
            - (string) index name: nombre de la collection

        Returns
            - (string o None) El posible contexto (documento) encontrado
        """
        try:
            collection = self.client.get_collection(index_name)
            results = collection.query(self.embedding_model.embed_query(text), n_results=1)
            context = results['documents'][0]
        except Exception:
            context = None

        return context
    
    def _get_question(self, text: str, index_name: str = "similarity_context", similarity_th: int = None) -> Union[str, None]:
        """
        Devuelve el contexto (pregunta) que se recupere de la colección <index_name>

        Args
            - (string) text: texto a buscar similaridades
            - (string) index name: nombre de la collection
            - (int) similarity_th: indica el theshold de similitud para la pregunta (menos de este y no se coge)

        Returns
            - (string o None) El posible contexto (documento) encontrado
        """
        try:
            collection = self.client.get_collection(index_name)
            results = collection.query(self.embedding_model.embed_query(text), n_results=1)
            context = results['documents'][0]
            re_exp = regex.compile(r"%QUESTION%.+") # regex para recuperar lo que aparece después
            context = re_exp.match(context).group(0)
            if similarity_th is not None:
                if results["distances"][0] < similarity_th:
                    context = None
        except Exception:
            context = None

        return context
    

    def add_question(self, context: str, question: str) -> None:
        """
        Añade contexto + pregunta a la bd vectorial permanente

        Args
            - (string) context: contexto a añadir
            - (string) question: pregunta resultante del contexto
        """
        collection = self.client.get_collection("similarity_context")
        text = "%CONTEXT%" + context + "%QUESTION%" + question # los guardamos con formato de token para evitar colisiones
        collection.add(
                ids= [str(uuid.uuid4())],
                embeddings=[self.embedding_model.embed_query(text)],
        )