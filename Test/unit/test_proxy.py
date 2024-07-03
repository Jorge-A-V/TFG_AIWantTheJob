import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import Mock, patch
from backend.modelo_ia.engine_proxy import Proxy
from backend.database.database import DataBase

@pytest.fixture
def mock_database():
    return Mock(spec=DataBase)

@pytest.fixture
def proxy(mock_database):
    with patch('backend.modelo_ia.engine_proxy.VectoreStore'), \
         patch('backend.modelo_ia.engine_proxy.NemoConfig'), \
         patch('backend.modelo_ia.engine_proxy.LLM'), \
         patch('backend.modelo_ia.engine_proxy.NemoCore'), \
         patch('backend.modelo_ia.engine_proxy.Cache'):
        return Proxy(database=mock_database)

def test_proxy_initialization(proxy):
    assert proxy.database is not None
    assert proxy.llm is not None
    assert proxy.nemo_system is not None
    assert proxy.cache is not None

@pytest.mark.asyncio
async def test_get_data_example(proxy):
    async def _mock_processCall(*args, **kwargs): return {"content": "Example response"}
    proxy.cache.get_content = _mock_processCall
    result = await proxy.get_data("test", "example", "user1")
    assert result == {"respuesta": "Example response"}

@pytest.mark.asyncio
async def test_get_data_question(proxy):
    async def _mock_processCall(*args, **kwargs): return {"content": "Generated question"}
    proxy.nemo_system.processCall = _mock_processCall

    proxy.nemo_system.db.add_question = Mock()
    proxy.cache.prepare_example = Mock()
    
    result = await proxy.get_data("context", "question", "user1")
    
    assert result == {"respuesta": "Generated question"}
    proxy.nemo_system.db.add_question.assert_called_once_with(context="context", question="Generated question")
    proxy.cache.prepare_example.assert_called_once_with("Generated question")

@pytest.mark.asyncio
async def test_get_data_answer(proxy):
    async def _mock_processCall(*args, **kwargs): return {"content": "Generated answer with score 8"}
    proxy.nemo_system.processCall = _mock_processCall
    
    with patch('backend.modelo_ia.engine_proxy.NumberGrabber') as mock_number_grabber:
        mock_number_grabber.return_value.grab_number.return_value = 8
        proxy.insertar_valor_array = Mock(return_value={"array": [8]})
        
        result = await proxy.get_data("answer text", "answer", "user1")
        
        assert result == {"respuesta": "Generated answer with score 8", "array": [8]}
        proxy.insertar_valor_array.assert_called_once_with("user1", 8)

def test_registrar_usuario(proxy, mock_database):
    mock_database.registrar_usuario.return_value = "user123"
    result = proxy.registrar_usuario("testuser", "password")
    assert result == {"id": "user123"}
    
    mock_database.registrar_usuario.return_value = "Name probably registered or internal error"
    result = proxy.registrar_usuario("existinguser", "password")
    assert result is None

def test_validar_usuario(proxy, mock_database):
    mock_database.validar_usuario.return_value = "user123"
    result = proxy.validar_usuario("testuser", "password")
    assert result == {"id": "user123"}
    
    mock_database.validar_usuario.return_value = "Error on validation"
    result = proxy.validar_usuario("wronguser", "wrongpassword")
    assert result is None

def test_insertar_valor_array(proxy, mock_database):
    mock_database.insertar_valor_array.return_value = [1, 2, 3, 4]
    result = proxy.insertar_valor_array("user123", 4)
    assert result == {"array": [1, 2, 3, 4]}

def test_recuperar_valores_array(proxy, mock_database):
    mock_database.recuperar_valores_array.return_value = [1, 2, 3]
    result = proxy.recuperar_valores_array("user123")
    assert result == {"array": [1, 2, 3]}