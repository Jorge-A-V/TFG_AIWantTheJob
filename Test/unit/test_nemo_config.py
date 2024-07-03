import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from backend.modelo_ia.nemo_config import NemoConfig

# Nombre arbitrario
model_name = "huggingface/model"

def crear_mock(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def test_init():
    config = NemoConfig(model_name)
    assert config.COLANG_CONFIG is not None
    assert 'path:' in config.YAML_CONFIG
    assert 'engine:' in config.YAML_CONFIG

def test_colang_no_existe():
    with pytest.raises(FileNotFoundError):
        NemoConfig(model_name)._set_colang_config('nonexistent_file.co')

