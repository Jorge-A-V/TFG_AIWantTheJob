import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from backend.api.api import app, init, get_health, subirarchivo, peticion, login, register, array_post, array_get

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] in ['available', 'loading']

def test_subirarchivo(client):
    with patch('backend.api.api.ftp_server') as mock_ftp_server:
        mock_ftp_server.get_data_as_dic.return_value = {"test": "data"}
        response = client.get('/subirarchivo')
        assert response.status_code == 200
        assert response.json == {"test": "data"}

def test_peticion(client):
    with patch('backend.api.api.system_proxy') as mock_system_proxy:
        async def _gd(*args, **kwargs): return {"respuesta": "test response", "array": [1, 2, 3]}
        mock_system_proxy.get_data = _gd
        response = client.get('/peticion/1?pregunta=test&modo=question')
        assert response.status_code == 200
        assert "respuesta" in response.json
        assert "array" in response.json

def test_login(client):
    with patch('backend.api.api.system_proxy') as mock_system_proxy:
        mock_system_proxy.validar_usuario.return_value = {"id": "test_id"}
        response = client.get('/login?user=test_user&password=test_password')
        assert response.status_code == 200
        assert response.json == {"id": "test_id"}

def test_login_fallo(client):
    with patch('backend.api.api.system_proxy') as mock_system_proxy:
        mock_system_proxy.validar_usuario.return_value = None
        response = client.get('/login?user=test_user&password=test_password')
        print(response)
        assert response.status_code == 200
        assert response.json == {"id": None}

def test_register(client):
    with patch('backend.api.api.system_proxy') as mock_system_proxy:
        mock_system_proxy.registrar_usuario.return_value = {"id": "new_test_id"}
        response = client.get('/register?user=new_user&password=new_password')
        assert response.status_code == 200
        assert response.json == {"id": "new_test_id"}

def test_register_fallo(client):
    with patch('backend.api.api.system_proxy') as mock_system_proxy:
        mock_system_proxy.registrar_usuario.return_value = None
        response = client.get('/register?user=new_user&password=new_password')
        assert response.status_code == 200
        assert response.json == {"id": None}

def test_array_post(client):
    with patch('backend.api.api.system_proxy') as mock_system_proxy:
        mock_system_proxy.insertar_valor_array.return_value = {"array": [1, 2, 3, 4]}
        response = client.get('/array_post?id=test_id&value=4')
        assert response.status_code == 200
        assert response.json == {"array": [1, 2, 3, 4]}

def test_array_get(client):
    with patch('backend.api.api.system_proxy') as mock_system_proxy:
        mock_system_proxy.recuperar_valores_array.return_value = {"array": [1, 2, 3]}
        response = client.get('/array_get?id=test_id')
        assert response.status_code == 200
        assert response.json == {"array": [1, 2, 3]}

def test_init():
    mock_proxy = MagicMock()
    mock_ftp_server = MagicMock()
    result = init(mock_proxy, mock_ftp_server)
    assert isinstance(result, Flask)