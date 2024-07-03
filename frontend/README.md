# Distribución de contenidos del frontend

Frontend define la aplicación con la que va a interactuar el usuario en tiempo de ejecución. Es una aplicación basada en estados que interactua con la api a través de una interfaz definida

```sh
| /frontend
| --> index.py
| --> setup.py
| --> README.md
| --> /helpers
|     --> api_functions.py
|     --> file_reader.py
|     --> ftp_client.py
```

# index.py

Define la página web principal con la que va a interactuar el usuario. La página se compromete de tres subsecciones:

Login y Register son las funciones de inicio de sesion y/o registro típicas de una aplicación

El chatbot viene a continuación

## setup.py

Define el modulo y los requisitos a instalar para esta parte del código

Para instalar manualmente (no recomendado)

```sh
cd frontend/
pip install . 
```

## README.md

Este fichero

# /helpers/

## api_functions.py

Define una interfaz para poder interactuar con la api a través del frontend.

Funciones de interés

```py
interfaz_api = API_helper(...)

# Funciones para pregunta/respuesta/ejemplo
interfaz_api.query_question(json_payload)
            .query_example_response(json_payload)
            .query_for_grading(json_payload)

# Pedir los detalles del ftpserver
interfaz_api.rag_query()

# Funcion de chequeo de salud
interfaz_api.start_health_checker(target=funcion_a_ejecutar)

# Funciones de la bd
interfaz_api.login(user, password)
            .register(user, password)
            .get_array(id)
            .post_array(id, valor)
```

## file_reader.py

Sirve para hacer el procesado rapido del pdf a subir desde el lector de ficheros del frontend

Funciones de interés:

```py
# Lectura de fichero
FileReader.read(fichero) -> BytesIO
```

## ftpclient.py

Sirve para realizar las conexiones con el ftp server (somos el client-side)

Funciones de interés

```py
cliente = FTPclient(...)

#Subida de archivo
cliente.upload_file(fichero)
```