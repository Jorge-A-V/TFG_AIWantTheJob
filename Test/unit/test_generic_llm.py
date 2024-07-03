import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from unittest.mock import MagicMock, patch
from backend.modelo_ia.generic_llm import LLM
import torch

@pytest.fixture
def mock_cuda():
    with patch('backend.modelo_ia.generic_llm.cuda') as mock:
        mock.is_available.return_value = True
        mock.current_device.return_value = 0
        yield mock

@pytest.fixture
def mock_transformers():
    with patch('backend.modelo_ia.generic_llm.transformers') as mock:
        mock.BitsAndBytesConfig.return_value = MagicMock()
        mock.AutoConfig.from_pretrained.return_value = MagicMock()
        mock.AutoModelForCausalLM.from_pretrained.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_tokenizer():
    with patch('backend.modelo_ia.generic_llm.AutoTokenizer') as mock:
        mock_tokenizer = MagicMock()
        mock_tokenizer.chat_template = None
        mock.from_pretrained.return_value = mock_tokenizer
        yield mock

@pytest.fixture
def mock_pipeline():
    with patch('backend.modelo_ia.generic_llm.pipeline') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_huggingface_pipeline_compatible():
    with patch('backend.modelo_ia.generic_llm.HuggingFacePipelineCompatible') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_llm_chain():
    with patch('backend.modelo_ia.generic_llm.LLMChain') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def llm(mock_cuda, mock_transformers, mock_tokenizer, mock_pipeline, mock_huggingface_pipeline_compatible, mock_llm_chain):
    return LLM()

def test_llm_initialization(llm):
    assert llm.question_response is not None
    assert llm.emulate_answer is not None
    assert llm.punctuate_answer is not None
    assert llm.llm is not None

def test_model_start_4bit(mock_cuda, mock_transformers, mock_tokenizer, mock_pipeline, mock_huggingface_pipeline_compatible, mock_llm_chain):
    llm = LLM(loading_mode="4bit")
    mock_transformers.BitsAndBytesConfig.assert_called_once_with(
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )

def test_model_start_8bit(mock_cuda, mock_transformers, mock_tokenizer, mock_pipeline, mock_huggingface_pipeline_compatible, mock_llm_chain):
    llm = LLM(loading_mode="8bit")
    mock_transformers.BitsAndBytesConfig.assert_called_once_with(
        load_in_8bit=True,
    )

def test_model_start_no_cuant(mock_cuda, mock_transformers, mock_tokenizer, mock_pipeline, mock_huggingface_pipeline_compatible, mock_llm_chain):
    llm = LLM(loading_mode="No cuant")
    mock_transformers.AutoModelForCausalLM.from_pretrained.assert_called_once_with(
        "meta-llama/Llama-2-7b-chat-hf", torch_dtype=torch.float16, trust_remote_code=True, device_map="auto"
    )

def test_set_default_callbacks(llm):
    llm._set_default_callbacks()
    assert callable(llm.question_response)
    assert callable(llm.emulate_answer)
    assert callable(llm.punctuate_answer)

@pytest.mark.asyncio
async def test_set_callback(llm):
    # Create a custom async function to mock LLMChain.invoke
    def mock_invoke(inputs):
        return {"text": "Test response"}

    mock_llm_chain = MagicMock()
    mock_llm_chain.invoke = mock_invoke
    
    with patch('backend.modelo_ia.generic_llm.LLMChain', return_value=mock_llm_chain):
        callback = llm._set_callback("Test system prompt")
        assert callable(callback)
        
        response = await callback("Test input")
        assert response == "Test response"

def test_get_chat_template_with_chat_template(llm):
    llm.tokenizer.chat_template = "Test chat template"
    llm.tokenizer.apply_chat_template.return_value = "Applied chat template"
    
    messages = [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "User message"}
    ]
    
    template = llm._get_chat_template(messages)
    assert template == "Applied chat template"
    llm.tokenizer.apply_chat_template.assert_called_once_with(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

def test_get_chat_template_without_chat_template(llm):
    llm.tokenizer.chat_template = None
    llm.tokenizer.apply_chat_template.return_value = "Applied chat template"
    
    messages = [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "User message"}
    ]
    
    template = llm._get_chat_template(messages)
    assert template == "Applied chat template"
    llm.tokenizer.apply_chat_template.assert_called_once_with(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

def test_get_chat_template_exception_handling(llm):
    llm.tokenizer.chat_template = "Test chat template"
    llm.tokenizer.apply_chat_template.side_effect = [Exception("Test exception"), "Applied chat template"]
    
    messages = [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "User message"}
    ]
    
    template = llm._get_chat_template(messages)
    assert template == "Applied chat template"
    assert llm.tokenizer.apply_chat_template.call_count == 2
