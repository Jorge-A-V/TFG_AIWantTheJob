import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from backend.modelo_ia.prompt_templates import PromptTemplates

def test_entrevistador_modo_pregunta():
    assert hasattr(PromptTemplates, 'question_sysprompt_template')
    assert isinstance(PromptTemplates.question_sysprompt_template, str)


def test_entrevistador_modo_ejemplo():
    assert hasattr(PromptTemplates, 'give_example_output_sysprompt_template')
    assert isinstance(PromptTemplates.give_example_output_sysprompt_template, str)

def test_entrevistador_modo_evaluacion():    
    assert hasattr(PromptTemplates, 'punctuate_answer_sysprompt_template')
    assert isinstance(PromptTemplates.punctuate_answer_sysprompt_template, str)

def test_template_de_phi():
    assert hasattr(PromptTemplates, 'phi1template')
    assert isinstance(PromptTemplates.phi1template, str)