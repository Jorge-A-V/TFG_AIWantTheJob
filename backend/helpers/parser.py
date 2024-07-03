import argparse
from typing import DefaultDict

def parser() -> DefaultDict[str, str]:
    """
    Funcion para parsear la entrada de texto, lo transforma en un diccionario que se puede desempaquetar en proxy

    Returns
        - (diccionario) desempaquetable en proxy
    """
    parser = argparse.ArgumentParser(description='Argumentos para el modelo')
    parser.add_argument('token', type=str, help='Token the hugging')
    parser.add_argument('-n', '--model_name', type=str, help="Nombre del repositorio de huggingface del modelo", required=False)
    parser.add_argument('-c', '--cuantization', type=str, help="Cuatizacion: 4bit o 8bit", required=False)
    
    args = parser.parse_args()
    token = args.token
    model_name = args.model_name if args.model_name is not None else "meta-llama/Llama-2-7b-chat-hf"#"microsoft/Phi-3-mini-4k-instruct"#"meta-llama/Meta-Llama-3-8B-Instruct"#
    cuantization = args.cuantization if args.cuantization is not None else "4bit"#"4bit"

    return {
        "token": token,
        "model_name": model_name,
        "cuantization": cuantization,
    }