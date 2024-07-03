import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from backend.helpers.parser import parser

def test_parser_por_defecto(monkeypatch):
    monkeypatch.setattr('sys.argv', ['script_name', 'test_token'])
    result = parser()
    assert result['token'] == 'test_token'
    assert result['model_name'] == 'meta-llama/Llama-2-7b-chat-hf'
    assert result['cuantization'] == '4bit'

def test_parser_valores_custom(monkeypatch):
    monkeypatch.setattr('sys.argv', ['script_name', 'test_token', '-n', 'custom_model', '-c', '8bit'])
    result = parser()
    assert result['token'] == 'test_token'
    assert result['model_name'] == 'custom_model'
    assert result['cuantization'] == '8bit'

def test_parser_sin_token(monkeypatch):
    monkeypatch.setattr('sys.argv', ['script_name'])
    with pytest.raises(SystemExit):
        parser()

def test_parser_argumento_equivocado(monkeypatch):
    monkeypatch.setattr('sys.argv', ['script_name', 'test_token', '--invalid_arg', 'value'])
    with pytest.raises(SystemExit):
        parser()
