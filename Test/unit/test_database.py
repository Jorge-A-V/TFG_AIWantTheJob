import pytest
import sqlite3
import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))


from backend.database.database import DataBase

import pytest
import sqlite3
from unittest.mock import patch, MagicMock

@pytest.fixture
def db():
    with patch('sqlite3.connect') as mock_connect:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        yield DataBase()

def test_init(db):
    assert db.connection is not None
    assert db.cursor is not None
    db.cursor.execute.assert_called_with('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY,
                            username TEXT,
                            password TEXT,
                            salt TEXT,
                            identifier TEXT UNIQUE,
                            CONSTRAINT unique_username_password UNIQUE (username, password))''')

def test_generate_identifier(db):
    identifier = db._generate_identifier("test_user", "test_password")
    assert isinstance(identifier, str)
    assert identifier.startswith('"')
    assert identifier.endswith('"')

def test_hash_password(db):
    password = "test_password"
    hashed_password, salt = db._hash_password(password)
    assert isinstance(hashed_password, str)
    assert isinstance(salt, str)

def test_registrar_usuario_success(db):
    db.cursor.fetchone.return_value = None
    db._generate_identifier = MagicMock(return_value='"test_id"')
    db._hash_password = MagicMock(return_value=("hashed_password", "salt"))
    
    result = db.registrar_usuario("test_user", "test_password")
    
    assert result == '"test_id"'
    db.cursor.execute.assert_any_call("SELECT username FROM users WHERE username = ?", ("test_user",))
    db.cursor.execute.assert_any_call("INSERT INTO users (username, password, salt, identifier) VALUES (?, ?)", ("test_user", "hashed_password", "salt", '"test_id"'))
    db.connection.commit.assert_called_once()

def test_registrar_usuario_existing_user(db):
    db.cursor.fetchone.return_value = ("existing_user",)
    
    result = db.registrar_usuario("existing_user", "test_password")
    
    assert result == "Name probably registered or internal error"
    db.connection.rollback.assert_not_called()

def test_registrar_usuario_error(db):
    db.cursor.fetchone.return_value = None
    db.cursor.execute.side_effect = sqlite3.Error("Test error")
    
    result = db.registrar_usuario("test_user", "test_password")
    
    assert result == "Name probably registered or internal error"
    db.connection.rollback.assert_called_once()

def test_validar_usuario_success(db):
    db.cursor.fetchone.return_value = ("hashed_password", "salt", "identifier")
    db._hash_password = MagicMock(return_value=("hashed_password", "salt"))
    
    result = db.validar_usuario("test_user", "test_password")
    
    assert result == "identifier"

def test_validar_usuario_fail(db):
    db.cursor.fetchone.return_value = ("wrong_hash", "salt", "identifier")
    db._hash_password = MagicMock(return_value=("hashed_password", "salt"))
    
    result = db.validar_usuario("test_user", "wrong_password")
    
    assert result == "Error on validation"

def test_validar_usuario_not_found(db):
    db.cursor.fetchone.return_value = None
    
    result = db.validar_usuario("non_existent_user", "test_password")
    
    assert result == "Error on validation"

def test_insertar_valor_array_success(db):
    db.recuperar_valores_array = MagicMock(return_value=[(1, 10.0), (2, 20.0)])
    
    result = db.insertar_valor_array("test_id", 30)
    
    assert result == [(1, 10.0), (2, 20.0)]
    db.cursor.execute.assert_called_with('INSERT INTO test_id (value) VALUES (?)', (30,))
    db.connection.commit.assert_called_once()

def test_insertar_valor_array_error(db):
    db.cursor.execute.side_effect = sqlite3.Error("Test error")
    db.recuperar_valores_array = MagicMock(return_value=[(0, 0.0)])
    
    result = db.insertar_valor_array("test_id", 30)
    
    assert result == [(0, 0.0)]
    db.connection.rollback.assert_called_once()

def test_recuperar_valores_array_success(db):
    db.cursor.fetchall.return_value = [(1, 10.0), (2, 20.0)]
    
    result = db.recuperar_valores_array("test_id")
    
    assert result == [(1, 10.0), (2, 20.0)]
    db.cursor.execute.assert_called_with('SELECT * FROM test_id ')

def test_recuperar_valores_array_error(db):
    db.cursor.execute.side_effect = sqlite3.Error("Test error")
    
    result = db.recuperar_valores_array("test_id")
    
    assert result == [(0, 0.0)]

def test_close(db):
    db.close()
    db.connection.close.assert_called_once()