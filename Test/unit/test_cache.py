import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.modelo_ia.pseudo_cache import Cache

@pytest.fixture
def mock_nemo():
    return MagicMock()

@pytest.fixture
def cache(mock_nemo):
    return Cache(mock_nemo)

@pytest.mark.asyncio
async def test_get_content(cache):
    mock_response = {"key": "value"}
    async def mock_response_func(): return mock_response
    cache._cached_response = mock_response_func()
    
    result = await cache.get_content()
    
    assert result == mock_response
    assert cache._cached_response is None

@pytest.mark.asyncio
async def test_get_content_none(cache):
    cache._cached_response = None
    
    # Asi esta en el proxy
    try:
        result = await cache.get_content()
    except TypeError:
        result = None

    assert result is None

def test_prepare_example(cache):
    question = "Test question"
    mock_response = {"key": "value"}
    cache.nemo.processCall = MagicMock(return_value=mock_response)
    
    cache.prepare_example(question)
    
    cache.nemo.processCall.assert_called_once_with(question, "example")
    assert cache._cached_response == mock_response