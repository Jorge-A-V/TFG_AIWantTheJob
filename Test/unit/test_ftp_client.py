import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import ftplib
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from frontend.helpers.ftpclient import FTPclient

@pytest.fixture
def ftp_client():
    with patch('frontend.helpers.ftpclient.ftplib.FTP'):
        return FTPclient("localhost", "9999", "user", "password")

def test_init(ftp_client):
    assert ftp_client.address == "localhost"
    assert ftp_client.port == "9999"
    assert ftp_client.user == "user"
    assert ftp_client.password == "password"
    assert ftp_client.ftp is not None

def test_start(ftp_client):
    ftp_client.ftp.connect.assert_called_once_with("localhost", "9999")
    ftp_client.ftp.login.assert_called_once_with("user", "password")

@patch('frontend.helpers.ftpclient.FileReader.read')
def test_upload_file(mock_file_reader, ftp_client):
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    
    mock_file_obj = BytesIO(b"Test content")
    mock_file_reader.return_value = mock_file_obj
    
    ftp_client.upload_file(mock_file)
    
    mock_file_reader.assert_called_once_with(mock_file)
    ftp_client.ftp.storbinary.assert_called_once_with('STOR test.txt', mock_file_obj)
    ftp_client.ftp.quit.assert_called_once()

@patch('frontend.helpers.ftpclient.ftplib.FTP')
def test_init_connection_error(mock_ftp):
    mock_ftp.return_value.connect.side_effect = ftplib.error_perm("Connection error")
    
    with pytest.raises(ftplib.error_perm):
        FTPclient("localhost", "9999", "user", "password")

@patch('frontend.helpers.ftpclient.FileReader.read')
def test_upload_file_error(mock_file_reader, ftp_client):
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    
    mock_file_obj = BytesIO(b"Test content")
    mock_file_reader.return_value = mock_file_obj
    
    ftp_client.ftp.storbinary.side_effect = ftplib.error_perm("Upload error")
    
    with pytest.raises(ftplib.error_perm):
        ftp_client.upload_file(mock_file)