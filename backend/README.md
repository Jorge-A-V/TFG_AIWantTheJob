# Distribución de archivos del backend

```sh
| backend/
| --> main.py
| --> setup.py
| --> README.md
| --> api
| --- --> api.py
|
| --> archivos/
|
| --> database/
| --- --> database.py
| --- --> data/
| --- --- --> sqlite databases
|
| --> helpers/
| --- --> ftpserver.py
| --- --> number_grabber.py
| --- --> parser.py
|
| --> modelo_ia/
| --- --> engine_proxy.py
| --- --> generic_llm.py
| --- --> nemo_config.py
| --- --> nemo_core.py
| --- --> prompt_template.py
| --- --> pseudo_cache.py
| --- --> vector_store.py
```

## main.py

Fichero principal que es el que runnea el programa

```py
python3 main.py "token_hugging"
```

## setup.py

Declara los requisitos y los paquetes de los modulos, en caso de querer instalarse simplemente esta parte del programa

```sh
cd backend
pip install .
```

## README.md

Este fichero

## archivos

Contiene el archivo que se va a usar como contexto general para el modelo (server-side). Es donde se suben los archivos del client side, también de contexto.

# Modelo IA

## engine_proxy.py

Intermediario absoluto del backend. Sirve para conectar cada uno de los componentes entre si

```py
proxy = Proxy(...)

# invocacón al modelo interno
proxy.get_data(texto, argumentos, id) 

# acceso (y operaciones) sobre la base de datos
proxy.registrar_usuario(nombre, contraseña)
     .validar_usuario(nombre, contraseña)
     .insertar_valor_array(user_id, valor)
     .recuperar_valores_array(user_id)
```

## generic_llm.py

Define de manera genérica un modelo de lenguaje (LLM) de huggingface. Permite al usuario instanciar cualquier tipo de modelo. 

Si el modelo es de tipo instruct y tiene *chat_template* habilitado es super simple, simplemente pones el nombre y ya está. Si el modelo NO tiene el chat_template, tienes que modificar el fichero en callback -> template al template de hugging que aparece en la página descriptiva del modelo:

```py
def _set_callback(self, sysprompt,
    template="copiar aquí template"
)
```

Funciones de interés

```py
modelo = LLM(...)

#definir un callback
callback = LLM._set_callback("sysprompt")

#usar el callback
respuesta = callback(pregunta)
```

## nemo_config.py

Define la estructura/configuración del engine del Nemo. Tocat la *COLANG CONFIG* si se quiere modificar el flujo de la conversación

```py
config = NemoConfig("nombre modelo")
```

## nemo_core.py

Core del sistema de nemo empleado. Basicamente se usa NemoGuardRails para guiar el flujo de conversación del agente (chatbot). En este archivo se define además como interactúa el LLM con el contexto (RAG).

```py
Nemo = NemoCore(...)

# metodo de uso
respuesta = Nemo.processCall(texto, argumento)

# actualización de la base de conocimientos del client-side
Nemo.update_db(path_al_document) # se sube con ftp
```

A la hora de registrar los callbacks dentro del nemo (*NemoGuardRails.register_action()*), primero le hacemos un setup de todos los contextos que tengamos definidos dentro de la base de datos vectorial

## prompt_template.py

Contiene strings absolutos que se corresponden a los sysprompts a emplear dentro del sistema.

Se pueden añadir todas las que uno quiera

```py
PromptTemplates.nombre_template
```

## pseudo_cache.py

Clase pensada para agilizar algunas consultas (ya que uno de los problemas de ejecutar esto en un portatil es la falta de velocidad).

La idea es pre-cargar alguna respuesta mientras el usuario hace tareas en el front para emular así una pre-carga de la cache. En este caso se pre-supone que si el usuario quiere una respuesta, ahorraremos algunos segundos mientras que si quiere una evaluación, la pre-carga (fallida) no causará delays porque acabará antes de que el usuario escriba su propia respuesta a evaluar.

```py
cache = Cache(...)

# preparar la cache
cache.prepare_example("pregunta")

# acceder al contenido (espera a que se carge si no ha terminado)
cache.get_context()
```

## vector_store.py

Clase base de datos vectorial basada en ChromaDB (uno de los nombres más estándar de la industria.) Chroma usa una base sqlite por detrás.

La idea es que la base de datos tenga 3 colleciones. Una del contexto del cliente, una del contexto del Servidor y una de preguntas.

Cliente y servidor son teóricamente volátiles mientras que la de preguntas es permanente.

```py
vs = VectorStore(...)

# subir un archivo a una colección
vs.load_and_embed("archivo", "nombre de la colección", ...)

# acceder a todos los contextos
vs.get_context("texto", ...)

# añadir una pregunta a la colección permanente
vs.add_question("contexto de la pregunta", "pregunta")
```

Si se quiere que cliente y servidor sean persistentes, borrar la siguiente linea:

```py
#VectorStore -> load_and_embed
try:
    # Borramos la colección si existe (no deberia ser permanente)
    self.client.delete_collection(index_name)
except Exception:
    pass
```

# api

En la carpeta de la api encontramos el desarrollo hecho con Flask de como el cliente se comunica con la propia api

## api.py

Define las siguientes rutas:

```py
# chequeo de salud de la api
@app.route("/health")

# devuelve los datos del servidor ftp para poder subir archivos a través de este
@app.route("/subirarchivo")

# Realiza una consulta al modelo
@app.route("/peticion/<id>")

# Operaciones de la base de datos
@app.route("/login")
@app.route("/register")
@app.route("/array_post")
@app.route("/array_get")
```

# Database

Empleamos una base de datos sqlite3 para poder guardar de manera arbitraria los datos de los usuarios

## database.py

```py
db = DataBase()

# registro de un usuario
db.registrar_usuario(self, nombre: str, password: str) -> id (str)

# validación de un usuario
db.validar_usuario(self, nombre: str, password: str) -> id (str)

# registro de un valor en el array de puntuaciones de un usuario
db.insertar_valor_array(self, identifier: str, value: int) -> List[Any] # (array de datos)

# recuperación del array de puntauaciones de un usuario
db.recuperar_valores_array(self, identifier: str) -> List[Any] # array de datos
```

## data/{sqlite databases}

Encontramos aquí las definiciones de la base de datos de clientes y la base de datos que usa chroma por detrás.

# Helpers

Encontramos aqui funciones auxiliares que se usan en algún que otro archivo para facilitar la comprensión. Equivalente al fichero "utils" común.

## ftpserver.py

Define el ftpserver que se tiene montado en el serverside para poder recibir los archivos que se suban desde el cliente.

```py
ftp = FTPserverEu()

# acceder a los datos del servidor
ftp.get_data_as_dic()

# cargar el handler
ftp.load(target="funcion a ejecutar on_load")

# iniciar el ftp_server en un hilo y devolver el hilo
hilo = ftp.start()
```

## parser.py

Usa argparse para devolver un diccionario desempaquetable como argumentos para *Proxy*

```py
def parser() ... # returns dict
```

```py
python3 archivo "token" -n "nombre modelo" -c "cuantización"
```

## number_grabber.py

Coge el primer número de un texto para establecerlo como nota de un valor.

Funciona en conjunto con el sysprompt de evaluación definido

```py
NumberGrabber.grab_number(texto) -> numero
```
