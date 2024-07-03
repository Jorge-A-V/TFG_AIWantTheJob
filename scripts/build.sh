#!/bin/bash

#Miniconda setup
conda create --name AIWantTheJob python==3.11 -y

#source to keep the enviroment in the terminal
source activate AIWantTheJob

#Setup poetry
pip install poetry

#dependency installs
poetry install

#Everything should run now