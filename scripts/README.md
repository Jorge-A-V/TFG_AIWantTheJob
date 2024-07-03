# Distribución de contenidos Scripts

Esta carpeta contiene los varios scripts a ejecutar para hacer el build de la aplicación y que runee perfectamente

```sh
| scripts/
| --> build.sh
| --> run.sh
| --> stop.sh
| --> conda_install.sh
| --> no_env_run.sh

```

## conda_install.sh

Instala el entorno de miniconda en el portatil para poder usar el metodo nº2 (entornos virtuales) para el runneo de la aplicación.

```sh
./conda_install.sh
exec bash #resetear la terminal
```

## build.sh

Sirve para constuir el el entorno de conda correcto una vez este conda instalado

```sh
./build.sh
```

## run.sh

Hace un run de la aplicación dentro del entorno de conda instalado para tener acceso a las librerías

```sh
./run.sh "token_de_hugging"
```

## stop.sh

Busca los procesos por nombre en el arbol de trabajo y los elimina manualmente. (Es posible que streamlit y sus hilos interactúen de manera rara con esto y se tenga que cerrar a mayores la pestaña del navegador)

```sh
./stop.sh
```

## no_env_run.sh

Hace un run de la aplicación directamente sobre los recursos del ordenador en ese momento (es decir no activa ningun tipo de virtualización). Es la manera más sencilla de hacer las cosas.

Requiere de instalar los requisitos:

```
requierements.txt
```

Es el fichero que se usa fuera de conda

```sh
./no_env_run.sh "token de hugging"
```

