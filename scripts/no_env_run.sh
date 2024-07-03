#!/bin/bash

# Backend
echo "Cargando backend..."
cd ../backend || exit
python3 main.py "$1" & #en segundo plano

# Frontend
echo "Cargando frontend..."
cd ../frontend || exit
streamlit run index.py
