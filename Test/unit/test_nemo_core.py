import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import MagicMock, patch
from backend.modelo_ia.nemo_core import NemoCore

@pytest.fixture
def mock_vector_store():
    return MagicMock()

@pytest.fixture
def mock_nemo_config():
    config = MagicMock()
    config.COLANG_CONFIG = "mock_colang_config"
    config.YAML_CONFIG = "mock_yaml_config"
    config.engine = "mock_engine"
    return config

@pytest.fixture
def mock_llm():
    return MagicMock()

@pytest.fixture
def nemo_core(mock_vector_store, mock_nemo_config, mock_llm):
    with patch('backend.modelo_ia.nemo_core.RailsConfig'), \
         patch('backend.modelo_ia.nemo_core.LLMRails'), \
         patch('backend.modelo_ia.nemo_core.get_llm_instance_wrapper'), \
         patch('backend.modelo_ia.nemo_core.register_llm_provider'), \
         patch('backend.modelo_ia.nemo_core.walk'):
        core = NemoCore(mock_vector_store, mock_nemo_config, mock_llm)
        core.rails = MagicMock()
        return core

def test_nemo_core_initialization(nemo_core, mock_vector_store, mock_nemo_config, mock_llm):
    assert nemo_core.db == mock_vector_store
    assert nemo_core.nemo_config == mock_nemo_config
    assert nemo_core.LLM == mock_llm
    assert nemo_core.rails is not None

def test_register_action(nemo_core):
    mock_callback = MagicMock()
    nemo_core.register_action(mock_callback, "test_action")
    nemo_core.rails.register_action.assert_called_once()

def test_register_actions(nemo_core):
    mock_callbacks = [MagicMock(), MagicMock(), MagicMock()]
    mock_names = ["action1", "action2", "action3"]
    mock_similarity_questions = [True, False, True]
    
    with patch.object(nemo_core, 'register_action') as mock_register_action:
        nemo_core.register_actions(mock_callbacks, mock_names, mock_similarity_questions)
        assert mock_register_action.call_count == 3

def test_set_context(nemo_core):
    nemo_core._get_context = MagicMock(return_value=("global_context", "client_context", "other_context"))
    result = nemo_core._set_context("test_text")
    assert "global_context" in result
    assert "client_context" in result
    assert "other_context" in result

def test_get_complete_args(nemo_core):
    question_args = nemo_core._get_complete_args("question")
    assert question_args["content"] == {"question": True, "answer": False, "example": False}
    
    answer_args = nemo_core._get_complete_args("answer")
    assert answer_args["content"] == {"question": False, "answer": True, "example": False}
    
    example_args = nemo_core._get_complete_args("example")
    assert example_args["content"] == {"question": False, "answer": False, "example": True}

@pytest.mark.asyncio
async def test_process_call(nemo_core):
    async def mock_gen_async(*args, **kwargs): return {"content": "Generated response"}
    nemo_core._get_complete_args = lambda *args, **kwargs: None
    nemo_core.rails.generate_async = mock_gen_async

    result = await nemo_core.processCall("test_text", "question")
    assert result == {"content": "Generated response"}

def test_update_db(nemo_core):
    with patch('os.remove') as mock_remove:
        nemo_core.update_db("test_document.txt")
        nemo_core.db.load_and_embed.assert_called_once_with("test_document.txt")
        mock_remove.assert_called_once_with("test_document.txt")

    nemo_core.db.load_and_embed.reset_mock()
    with patch('os.remove') as mock_remove:
        nemo_core.update_db("test_document.txt", remove=False)
        nemo_core.db.load_and_embed.assert_called_once_with("test_document.txt")
        mock_remove.assert_not_called()

def test_get_context(nemo_core):
    nemo_core.db.get_context.return_value = ("global", "client", "other")
    result = nemo_core._get_context("test_text", question=True)
    assert result == ("global", "client", "other")
    nemo_core.db.get_context.assert_called_once_with("test_text", True)