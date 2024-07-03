import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import MagicMock, patch
from backend.helpers.ftpserver import FTPserverEu

@pytest.fixture
def ftp_server():
    return FTPserverEu()

def test_init(ftp_server):
    assert ftp_server._usuario == "generic"
    assert ftp_server._password == "1234"
    assert ftp_server._direccion == "localhost"
    assert ftp_server._puerto == 9999
    assert ftp_server.server is None

def test_get_data_as_dic(ftp_server):
    data = ftp_server.get_data_as_dic()
    assert data == {
        "user": "generic",
        "password": "1234",
        "address": "localhost",
        "port": 9999,
    }

@patch('backend.helpers.ftpserver.FTPServer')
@patch('backend.helpers.ftpserver.FTPHandler')
def test_load(mock_ftp_handler, mock_ftp_server, ftp_server):
    mock_target = MagicMock()
    ftp_server.load(mock_target)
    
    assert ftp_server.server is not None
    mock_ftp_server.assert_called_once()
    # mock_ftp_handler no se calea que se pasa como clase (se tendria qeu iniciar el servidor manualmente en el hilo)

@patch('backend.helpers.ftpserver.FTPServer')
@patch('backend.helpers.ftpserver.FTPHandler')
def test_load_error(mock_ftp_handler, mock_ftp_server, ftp_server):
    mock_target = MagicMock()
    mock_ftp_server.side_effect = Exception("FTP Server error")
    
    with pytest.raises(Exception):
        ftp_server.load(mock_target)

@patch('threading.Thread')
def test_start(mock_thread, ftp_server):
    ftp_server.server = MagicMock()
    thread = ftp_server.start()
    
    mock_thread.assert_called_once()
    ftp_server.server.serve_forever.assert_not_called()  # se tiene que iniciar manualmente despues