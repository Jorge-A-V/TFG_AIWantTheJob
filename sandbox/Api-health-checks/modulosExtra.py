import argparse

def parser():
    parser = argparse.ArgumentParser(description='Se necesita el token de huggin')
    parser.add_argument('input_string', type=str, help='Token the huggin')
    
    args = parser.parse_args()
    input_string = args.input_string
    
    return input_string