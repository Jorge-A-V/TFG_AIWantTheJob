import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import MagicMock, patch
from backend.modelo_ia.vector_store import VectoreStore

@pytest.fixture
def mock_chromadb_client():
    with patch('backend.modelo_ia.vector_store.chromadb.PersistentClient') as mock_client:
        yield mock_client

@pytest.fixture
def instancia_mockeada(mock_chromadb_client):
    return VectoreStore()

def test_init(instancia_mockeada, mock_chromadb_client):
    assert instancia_mockeada.client == mock_chromadb_client.return_value
    assert instancia_mockeada.embedding_model is not None

def test_start_embd_model(instancia_mockeada):
    model = instancia_mockeada._start_embd_model("sentence-transformers/all-MiniLM-L6-v2")
    assert model is not None

def test_load_and_embed(instancia_mockeada):
    with patch('backend.modelo_ia.vector_store.PDFMinerLoader') as mock_loader, \
         patch('backend.modelo_ia.vector_store.RecursiveCharacterTextSplitter') as mock_splitter, \
         patch('backend.modelo_ia.vector_store.HuggingFaceEmbeddings.embed_documents') as mock_embed_documents:
        
        mock_loader_instance = mock_loader.return_value
        mock_splitter_instance = mock_splitter.return_value

        content_mock = [MagicMock(page_content="content")]
        split_mock = [MagicMock(page_content="split_content")]
        mock_loader_instance.load.return_value = content_mock
        mock_splitter_instance.split_documents.return_value = split_mock

        instancia_mockeada.load_and_embed("document_route")

        mock_loader_instance.load.assert_called_once_with()
        mock_splitter_instance.split_documents.assert_called_once_with(content_mock)
        mock_embed_documents.assert_called_once_with(["split_content"])

def test_get_context(instancia_mockeada):
    with patch.object(instancia_mockeada, '_get_document', return_value="context") as mock_get_document, \
         patch.object(instancia_mockeada, '_get_question', return_value="question") as mock_get_question:

        general_context, client_context, similarity_context = instancia_mockeada.get_context("text", question=True)
        
        assert general_context == "context"
        assert client_context == "context"
        assert similarity_context == "question"

        mock_get_document.assert_any_call("text", "general_context")
        mock_get_document.assert_any_call("text", "client_context")
        mock_get_question.assert_called_once_with("text", "similarity_context")

def test_get_document(instancia_mockeada):
    with patch.object(instancia_mockeada.client, 'get_collection') as mock_get_collection:
        mock_collection = mock_get_collection.return_value
        mock_collection.query.return_value = {'documents': ["document"]}

        context = instancia_mockeada._get_document("text", "index_name")
        assert context == "document"

def test_get_document_exception(instancia_mockeada):
    with patch.object(instancia_mockeada.client, 'get_collection', side_effect=Exception):
        context = instancia_mockeada._get_document("text", "index_name")
        assert context is None

def test_get_question(instancia_mockeada):
    with patch.object(instancia_mockeada.client, 'get_collection') as mock_get_collection, \
         patch('backend.modelo_ia.vector_store.regex.compile') as mock_regex_compile:
        
        mock_collection = mock_get_collection.return_value
        mock_collection.query.return_value = {'documents': ["%QUESTION%question"], "distances": [0.5]}
        mock_match = MagicMock()
        mock_match.group.return_value = "question"
        mock_regex_compile.return_value.match.return_value = mock_match

        context = instancia_mockeada._get_question("text", "index_name", similarity_th=0.6)
        assert context is None

        context = instancia_mockeada._get_question("text", "index_name", similarity_th=0.4)
        assert context == "question"

def test_get_question_exception(instancia_mockeada):
    with patch.object(instancia_mockeada.client, 'get_collection', side_effect=Exception):
        context = instancia_mockeada._get_question("text", "index_name")
        assert context is None


def test_add_question(instancia_mockeada):
    with patch('backend.modelo_ia.vector_store.HuggingFaceEmbeddings.embed_query', return_value=[0.1, 0.2, 0.3]) as mock_embed_query, \
         patch.object(instancia_mockeada.client, 'get_collection') as mock_get_collection ,\
            patch("backend.modelo_ia.vector_store.uuid.uuid4", return_value = "embeddings") as mock_uuid:

        mock_collection = mock_get_collection.return_value

        instancia_mockeada.add_question("context", "question")
        
        mock_get_collection.assert_called_once_with("similarity_context")
        mock_embed_query.assert_called_once_with("%CONTEXT%context%QUESTION%question")
        mock_collection.add.assert_called_once_with(
            ids=["embeddings"],
            embeddings=[mock_embed_query.return_value]
        )
