import sys
from pathlib import Path

# Añadimos el directorio padre
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

import pytest
from backend.helpers.number_graber import NumberGrabber

@pytest.fixture
def grabber():
    return NumberGrabber()

def test_grab_un_numero(grabber):
    assert grabber.grab_number("The answer is 42") == 42

def test_grab_solo_primer_numero(grabber):
    assert grabber.grab_number("There are 3 apples and 5 oranges") == 3

def test_grab_sin_numeros(grabber):
    assert grabber.grab_number("There are no numbers here") == 0

def test_grab_number_negativo(grabber):
    assert grabber.grab_number("The temperature is -5 degrees") == 0 # no es entero

def test_grab_number_decimal(grabber):
    assert grabber.grab_number("The price is 10.99 dollars") == 0 # no es entero

def test_grab_number_string_vacio(grabber):
    assert grabber.grab_number("") == 0