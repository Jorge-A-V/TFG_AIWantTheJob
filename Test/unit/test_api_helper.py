import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import patch, MagicMock
from frontend.helpers.api_functions import API_helper

@pytest.fixture
def api_helper():
    return API_helper()

def test_init(api_helper):
    assert api_helper.id == 1
    assert api_helper._ip == "127.0.0.1"
    assert api_helper._port == "5000"
    assert api_helper.API_URL == "http://127.0.0.1:5000/peticion/"
    assert api_helper.HEALTH_URL == "http://127.0.0.1:5000/health"
    assert api_helper.RAG_URL == "http://127.0.0.1:5000/subirarchivo"

def test_set_id(api_helper):
    api_helper.set_id("new_id")
    assert api_helper.id == "new_id"

@pytest.mark.asyncio
async def test_api_query(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response

        result = await api_helper.api_query({"param": "value"}, "http://test.url")
        assert result == {"test": "data"}
        mock_get.assert_called_once_with(url="http://test.url", headers={}, params={"param": "value"})

@pytest.mark.asyncio
async def test_query_question(api_helper):
    with patch.object(api_helper, 'api_query') as mock_api_query:
        mock_api_query.return_value = {"respuesta": "test answer"}
        result = await api_helper.query_question({"test": "payload"})
        assert result == "test answer"
        mock_api_query.assert_called_once_with({"test": "payload", "modo": "question"}, api_helper.API_URL + "1")

@pytest.mark.asyncio
async def test_query_example(api_helper):
    with patch.object(api_helper, 'api_query') as mock_api_query:
        mock_api_query.return_value = {"respuesta": "test answer"}
        result = await api_helper.query_example_response({"test": "payload"})
        assert result == "test answer"
        mock_api_query.assert_called_once_with({"test": "payload", "modo": "example"}, api_helper.API_URL + "1")

@pytest.mark.asyncio
async def test_query_evaluation(api_helper):
    with patch.object(api_helper, 'api_query') as mock_api_query:
        mock_api_query.return_value = {"respuesta": "test answer", "array": [1,2]}
        result, array = await api_helper.query_for_grading({"test": "payload"})
        assert result == "test answer"
        assert array == [1,2]
        mock_api_query.assert_called_once_with({"test": "payload", "modo": "answer"}, api_helper.API_URL + "1")

@pytest.mark.asyncio
async def test_rag_query(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"address": "test_address", "port": "test_port", "user": "test_user", "password": "test_password"}
        mock_get.return_value = mock_response

        result = await api_helper.rag_query()
        assert result == ("test_address", "test_port", "test_user", "test_password")
        mock_get.assert_called_once_with(api_helper.RAG_URL)

@pytest.mark.asyncio
async def test_login_bien(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test_id"}
        mock_get.return_value = mock_response

        result = await api_helper.login("test_user", "test_password")
        assert result == "test_id"
        mock_get.assert_called_once_with(api_helper.URL_BASE + api_helper.login_extension, params={"user": "test_user", "password": "test_password"})

@pytest.mark.asyncio
async def test_login_fallo(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("Fallo de Login")
        mock_get.return_value = mock_response

        result = await api_helper.login("test_user", "test_password")
        assert result is None

@pytest.mark.asyncio
async def test_register_bien(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test_id"}
        mock_get.return_value = mock_response

        result = await api_helper.register("test_user", "test_password")
        assert result == "test_id"
        mock_get.assert_called_once_with(api_helper.URL_BASE + api_helper.register_extension, params={"user": "test_user", "password": "test_password"})

@pytest.mark.asyncio
async def test_register_fallo(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("Fallo de registro")
        mock_get.return_value = mock_response

        result = await api_helper.register("test_user", "test_password")
        assert result is None

@pytest.mark.asyncio
async def test_get_array_bien(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test_id", "array": [1,2]}
        mock_get.return_value = mock_response

        result = await api_helper.get_array("test_id")
        assert result == [1,2]
        mock_get.assert_called_once_with(api_helper.URL_BASE + api_helper.get_array_extension, params={"id": "test_id"})

@pytest.mark.asyncio
async def test_get_array_mal(api_helper):
    with patch.object(api_helper._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("Get array fallo")
        mock_get.return_value = mock_response

        result = await api_helper.get_array("test_id")
        assert result == [(0, 0.0), ]