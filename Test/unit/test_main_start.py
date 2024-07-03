import pytest
from unittest.mock import MagicMock, patch

import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

@pytest.fixture
def mock_imports(monkeypatch):
    mock_ftpserver = MagicMock()
    mock_database = MagicMock()
    mock_proxy_login = MagicMock()
    mock_proxy = MagicMock()
    mock_init = MagicMock()
    mock_parser = MagicMock()
    mock_hf_login = MagicMock()

    monkeypatch.setattr("backend.modelo_ia.engine_proxy.login", mock_proxy_login)
    monkeypatch.setattr('backend.helpers.ftpserver.FTPserverEu', mock_ftpserver)
    monkeypatch.setattr('backend.database.database.DataBase', mock_database)
    monkeypatch.setattr('backend.modelo_ia.engine_proxy.Proxy', mock_proxy)
    monkeypatch.setattr('backend.api.api.init', mock_init)
    monkeypatch.setattr('backend.helpers.parser.parser', mock_parser)
    monkeypatch.setattr('huggingface_hub._login', mock_hf_login)

    from backend.main import main

    return mock_ftpserver, mock_database, mock_proxy, mock_init, mock_parser, mock_hf_login, mock_proxy_login, main

def test_main_script(mock_imports):
    mock_ftpserver, mock_database, mock_proxy, mock_init, mock_parser, mock_hf_login, mock_proxy_login, main = mock_imports

    # Set up mock returns
    mock_parser.return_value = {'token': 'fake_test_token', 'model_name': 'test_model', 'cuantization': '4bit'}
    mock_ftpserver_instance = MagicMock()
    mock_ftpserver.return_value = mock_ftpserver_instance
    mock_database_instance = MagicMock()
    mock_database.return_value = mock_database_instance
    mock_proxy_instance = MagicMock()
    mock_proxy.return_value = mock_proxy_instance
    mock_init_instance = MagicMock()
    mock_init.return_value = mock_init_instance

    # Import and run main
    with patch('backend.modelo_ia.engine_proxy.login') as mock_login:
        main()

    # Assert that the objects were created and methods were called
    mock_ftpserver.assert_called_once()
    mock_database.assert_called_once()
    mock_proxy.assert_called_once_with(**mock_parser.return_value, database=mock_database_instance)
    mock_ftpserver_instance.load.assert_called_once_with(target=mock_proxy_instance.nemo_system.update_db)
    mock_ftpserver_instance.start.assert_called_once()
    mock_init.assert_called_once_with(proxy=mock_proxy_instance, ftp_server_arg=mock_ftpserver_instance)
    mock_init_instance.run.assert_called_once_with(debug=False)
