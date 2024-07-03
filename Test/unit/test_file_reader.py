import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import MagicMock
from io import BytesIO

from frontend.helpers.file_reader import FileReader

def test_read():
    test_content = b"Test content"
    mock_file = BytesIO(test_content)
    
    result = FileReader.read(mock_file)
    
    assert isinstance(result, BytesIO)
    assert result.getvalue() == test_content

def test_read_error():
    mock_file = MagicMock()
    mock_file.read.side_effect = IOError("File read error")
    
    with pytest.raises(IOError):
        FileReader.read(mock_file)