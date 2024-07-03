#!/bin/bash

# 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

#Chequeamos por los argumentos
if [ $# -eq 0 ]; then
    echo "Se requiere un argumento => Método de uso: $0 <token_huggin>"
    exit 1
fi

# Nos movemos al entorno virtual
source activate AIWantTheJob

# Backend
echo "Cargando backend..."
cd ../backend || exit
python3 main.py "$1" & #en segundo plano

# Frontend
echo "Cargando frontend..."
cd ../frontend || exit
streamlit run index.py
