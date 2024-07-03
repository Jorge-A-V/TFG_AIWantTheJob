#https://github.com/AI-Yash/st-chat/blob/main/examples/chatbot.py
import sys
sys.path.append("../")

import streamlit as st
from streamlit_chat import message
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import asyncio
import pandas as pd

from frontend.helpers.api_functions import API_helper 
from frontend.helpers.ftpclient import FTPclient

from typing import List, Any, DefaultDict, Union

comentario = """
-----------------------------------------------------------------------
CONFIGURACIÓN Y HEADERS
-----------------------------------------------------------------------
"""

st.set_page_config(
    page_title="AIWantTheJob",
    page_icon=":robot:"
)

st.header("AIWantTheJob")
st.markdown("[Repositorio de Github](https://github.com/Jorge-A-V/TFG_AIWantTheJob.git)")

comentario = """
-----------------------------------------------------------------------
DECLARAMOS VARIABLES/ELEMETOS DEL SESSION STATE
-----------------------------------------------------------------------
"""

# api helpert es nuestra interfaz de la api
if "api_helper_init" not in st.session_state:
    st.session_state.api_helper_init = True
    st.session_state.api_helper = API_helper(id=1)

if 'id' not in st.session_state:
    st.session_state.id = "None"

if 'grade_array' not in st.session_state:
    st.session_state.grade_array = []

# deshabilitar ciertos elementos
if "disabled" not in st.session_state:
    st.session_state.disabled = False

if 'mode'  not in st.session_state:
    st.session_state.mode = "question"

if 'page' not in st.session_state:
    st.session_state.page = "login"

# mensajes del  bot
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hello, I am an interviewer assitant, how can i help you?"]

# mensajes del usuario
if 'past' not in st.session_state:
    st.session_state['past'] = ["Im the user"]

if 'credentials' not in st.session_state:
    st.session_state.credentials = None 
    #{"user": "user1", "password": "user1"}
    #get_id()

comentario = """
-----------------------------------------------------------------------
FUNCION PARA ESTANDARIZAR EL TAMAÑO DEL BOTON
-----------------------------------------------------------------------
"""
def crear_boton_estandar(
        label: str,
        on_click = lambda *args, **kwargs: None,
        args = None,
        key = None
):
    """
    Creamos un boton con la anchura estandarizada al tamaño de contenedor
    """
    return st.button(
        label,
        on_click=on_click,
        args=args,
        key=key,
        use_container_width=True,
    )

comentario = """
-----------------------------------------------------------------------
FUNCIONES PARA: Cambiar de mode/page y hacer triggering de enable/disable
-----------------------------------------------------------------------
"""

def set_mode_state(state: str) -> None:
    """
    Pone st.session_state["mode"] al valor de state
    """
    global st
    st.session_state["mode"] = state
    print(st.session_state.get("mode"))

def get_mode_state() -> str:
    """
    Devuelve st.session_state["mode"]
    """
    return st.session_state.get("mode")

def set_page_state(state: str) -> None:    
    """
    Pone st.session_state["page"] al valor de state
    """
    global st
    st.session_state["page"] = state
    print(st.session_state.get("page"))

def disable_enable() -> None:
    """
    Hace de interruptor 0/1 en diable de True <> False
    """
    status = st.session_state.get("disabled", True)
    if status:
        st.session_state["disabled"] = False
    else:
        st.session_state["disabled"] = True

def disable_components() -> None:
    """
    Deshabilita los componentes (st.session_state["disabled"])
    """
    st.session_state["disabled"] = True

def enable_components() -> None:
    """
    Habilita los componentes (st.session_state["disabled"])
    """
    st.session_state["disabled"] = False

comentario = """
-----------------------------------------------------------------------
HILO de health (no funciona por el streamlit)
-----------------------------------------------------------------------
"""

def do_on_heath(health: str) -> None:
    """
    Funcion que hace un disable/enable en base al estado de salud de la API.
    En este caso streamlit no funciona con hilos asi que es meramente simbolico

    Args:
        - (string) health: estado de salud
    """
    if health is None:
        disable_components()
    if health == "loading":
        disable_components()
    else:
        enable_components()

comentario = """
En la Documentación de streamlit sale que hay que meter al hilo en el contexto para que funcione
Pero hay varias issues que demuestran que los hilos no funcionan como deberia (basicamente usan
su propio contexto)
"""
health_thread = st.session_state.api_helper.start_health_checker(target=do_on_heath)
ctx = get_script_run_ctx()
add_script_run_ctx(thread=health_thread, ctx=ctx)
health_thread.start()

comentario = """
------------------------------------------------------------------------------
Funciones para llamar a la api y hacer login, registro y tratar con el array
------------------------------------------------------------------------------
"""

def get_id() -> None:
    """
    Se hace una conexión a la api realizando un login en base a las creedenciales del usuario en st.
    Se concatena con un get_grade_array() para cargar los valores.
    FUNCION PARA PRUEBAS
    """
    user, password = st.session_state.credentials["user"], st.session_state.credentials["password"]
    st.session_state.id = asyncio.run(st.session_state.api_helper.login(user, password))
    st.session_state.api_helper.set_id(st.session_state.id)
    get_grade_array()
            
def get_grade_array() -> None:
    """
    Hace una consulta a la api para obtener el array de notas asociado con el id de usuario actual
    """
    st.session_state.grade_array = asyncio.run(st.session_state.api_helper.get_array(st.session_state.id))

def set_grade_array(array: List[Any]) -> None:
    """
    Establece el valor de array en st.grade_array

    Args:
        - (array) array: lista de datos a actualizar
    """
    st.session_state.grade_array = array

def try_login(credentials: DefaultDict[str, str]) -> Union[str, None]:
    """
    Hace una consulta a la api intentando hacer un login con los credenciales
    Args
        - (diccionario) credentials: {user: ..., password: ...}

    Returns:
        - (string) the user id
    """
    id = asyncio.run(st.session_state.api_helper.login(credentials["user"], credentials["password"]))
    return id

def try_register(credentials: DefaultDict[str, str]) -> Union[str, None]:
    """
    Hace una consulta a la api intentando hacer un register con los credenciales
    Args
        - (diccionario) credentials: {user: ..., password: ...}

    Returns:
        - (string) the user id
    """
    id = asyncio.run(st.session_state.api_helper.register(credentials["user"], credentials["password"]))
    return id


comentario = """
-----------------------------------------------------------------------
Pagina login
-----------------------------------------------------------------------
"""

placeholder = st.empty()

if st.session_state.page == "login":

    #dentro del empty
    with placeholder.container():
        st.title('Login')
        username = st.text_input('Username', key="u1")
        password = st.text_input('Password', type='password', key="p1")
        
        _, col1, _ = st.columns([1,2,1])
        with col1:
            login = crear_boton_estandar('Login', key="login_button")
            goto_register = crear_boton_estandar("or register", key="goto_register_button")
        
        st.info('Please enter your credentials to login.')

    if login:
        credentials = {
            'user': username,
            'password': password
        }
        
        id = try_login(credentials)
        if id is not None:
            st.session_state.id = id
            st.session_state.api_helper.set_id(st.session_state.id)
            get_grade_array()
            placeholder.empty()
            st.session_state.page = "chat"
            st.experimental_rerun()
        else:
            st.error('Login failed. Please check your username and password.')

    if goto_register:
        placeholder.empty()
        st.session_state.page = "register"
        st.experimental_rerun()


comentario = """
-----------------------------------------------------------------------
Pagina de register
-----------------------------------------------------------------------
"""

if st.session_state.page == "register":

    with placeholder.container():
        st.title('Register')
        username = st.text_input('Username', key="u2")
        password = st.text_input('Password', type='password', key="p2")
        password_check = st.text_input('Password_check', type='password', key="p2c")
        
        _, col1, _ = st.columns([1,2,1])
        with col1:
            register = crear_boton_estandar('Register', key="register_button")
            goto_login = crear_boton_estandar("or login", key="goto_login_button")

        st.info('Please enter your credentials to register.')

    if register:

        if password != password_check:
            st.error("Passwords do not match")

        credentials = {
            'user': username,
            'password': password
        }
        
        id = try_register(credentials)
        if id is not None:
            st.session_state.id = id
            st.session_state.api_helper.set_id(st.session_state.id)
            get_grade_array()
            placeholder.empty()
            st.session_state.page = "tutorial"
            st.experimental_rerun()
        else:
            st.error('Register failed. Please check your username and password.')

    if goto_login:
        placeholder.empty()
        st.session_state.page = "login"
        st.experimental_rerun()
        
comentario = """
-----------------------------------------------------------------------
Pagina del tutorial
-----------------------------------------------------------------------
"""

if st.session_state.page == "tutorial":

    # Continue button in the top right
    _, col1 = st.columns([5, 1])
    with col1:
        if crear_boton_estandar("Continue", key="continue_to_chat"):
            st.session_state.page = "chat"
            st.experimental_rerun()

    st.title("Tutorial")
    st.write("We present the tutorial for the uso of this app. First as you have seen we have presented you with both")
    st.markdown("### Login")
    cont1 = st.empty()
    with cont1.container(border=True):
        st.image("./webapp_images/Login.png")

    st.markdown("### Register")
    cont2 = st.empty()
    with cont2.container(border=True):
        st.image("./webapp_images/Register.png")

    st.markdown("### Top-of-chat buttons")
    st.write("In the following page you will acess the chatbot")
    cont3 = st.empty()
    with cont3.container(border=True):
        st.image("./webapp_images/BotArribas.png")
    st.write("On top of the page you have access to a logout button and a tutorial button to come back here")

    st.markdown("### Interviewer Options")
    cont4 = st.empty()
    with cont4.container(border=True):
        st.image("./webapp_images/ChatBot.png")
    st.write("Following this we proceed with the chatbot")
    st.markdown("""We display the following options (from left to right)
                
 - Ask a bot for an example of a question
 - Answer the question and have the bot evaluate it
 - Ask the bot to answer the generated question for you
                
You may use the textBox above to write your answers (For option 3 no text is needed)
""")
    
    st.markdown("### File upload")
    cont5 = st.empty()
    with cont5.container(border=True):
        st.image("./webapp_images/SubirArchivo.png")
    st.write("Here we provide a file reader to upload your pdfs with knoledge you may need the intervviewer to have")

    st.markdown("### Grade History")
    cont6 = st.empty()
    with cont6.container(border=True):
        st.image("./webapp_images/Historial.png")
    st.write("Lastly we provide a grapth ranging from 0 to 5 that serves as a way of following your progress")


    
comentario = """
-----------------------------------------------------------------------
Pagina del chat
-----------------------------------------------------------------------
"""

if st.session_state.page == "chat":

    #botones arriba
    col1, _, col2 = st.columns([1, 4, 1])
    with col1:
        if crear_boton_estandar("Tutorial", key="goto_tutorial"):
            set_page_state("tutorial")
            st.experimental_rerun()
    with col2:
        if crear_boton_estandar("Logout", key="close_session"):
            # Reset session state and go back to login
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            set_page_state("login")
            st.experimental_rerun()

    # Esto es el chat, coge los mensajes de la lista y los imprime de arriba a abajo
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            try:
                message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            except Exception:
                pass
            try:
                message(st.session_state["generated"][i], key=str(i))
            except Exception:
                pass
    
    # input de mensajes del usuario
    user_input = st.text_input(label="ChatBox", key="input", disabled=st.session_state.get("disabled", True))

    def do_query_test() -> None:
        """
        Intenta realizar una query de tipo generar pregunta.
        Coge el input de usuario, lo ennvia a traves del api proxy como topico de la pregunta
        """
        st.session_state.past.append(user_input)
        output = asyncio.run(st.session_state.api_helper.query_question(prepare_query("Topic: " + user_input)))
        st.session_state["input"] = ""
        st.session_state["generated"].append(output)

    def do_response_test() -> None:
        """
        Intenta realizar una query de tipo generar evaluación a una respuesta.
        Coge el input de usuario, le pasa la combinación pregunta + respuesta a la api para que la evalue
        Recibe el array de notas actualizado, lo actualiza en el state
        """
        previa = st.session_state["generated"][-1]
        st.session_state.past.append(user_input)
        output, array = asyncio.run(st.session_state.api_helper.query_for_grading(prepare_query("Question: " + previa + "\n" + "Response: " + user_input)))
        set_grade_array(array)
        st.session_state["input"] = ""
        st.session_state["generated"].append(output)

    def do_dummy_response_test() -> None:
        """
        Intenta realizar una query de tipo responder a una pregunta generada.
        Coge el elemento (pregunta) que generó antes el modelo y lo envia para simular una respuesta
        """
        previa = st.session_state["generated"][-1]
        st.session_state.past.append("Give me an example to this question")
        st.session_state["input"] = ""
        output = asyncio.run(st.session_state.api_helper.query_example_response(prepare_query("Answer as an Example: " + previa)))
        st.session_state["generated"].append(output)

    def prepare_query(user_input: str) -> DefaultDict[str, str]:
        """
        Prepara el contenido (payload) metiendo user_input en un diccionario
        """
        return {"pregunta": user_input}

    comentario = """
-----------------------------------------------------------------
Esto es lo específico
------------------------------------------------------------------
"""

    def send_query(petition: str) -> None:
        """
        Realiza una acción de las definidas (pregunta, respuesta, simulación) en base al contexto
        Solo deja al usuario responder o simular si el modelo ha generado una respuesta anteriormente
        
        Args:
            - (string) peticion: tipo de petición
        """
        mode = get_mode_state()
        print(mode, petition)
        if petition == "question":
            do_query_test()
            set_mode_state("to_answer")
            print(st.session_state.get("mode"))
            print(get_mode_state())
            return
        if mode != "to_answer" and (petition == "answer" or petition == "example"):
            st.session_state["generated"].append("No interviewer question was asked, so i cannot give an example or evaluate an aswer to an invalid question")
            st.session_state["past"].append("<User Invalid Action>")
            return
        if petition == "answer":
            do_response_test()
            set_mode_state("question")
            return
        if petition == "example":
            do_dummy_response_test()
            set_mode_state("question")
            return


    # para poner los botones en paralelo y que no quede tan feo
    _, col1, _,  col2, _, col3, _ = st.columns([1,3,1,3,1,3,1])

    with col1:
        crear_boton_estandar("Ask for question", key="b_pregunta", on_click=send_query, args=["question"])
    
    with col2:
        crear_boton_estandar("Evaluate Answer", key="b_respuesta", on_click=send_query, args=["answer"])

    with col3:
        crear_boton_estandar("Ask for example", key="b_example", on_click=send_query, args=["example"])

    comentario = """
-------------------------------------------------------------------
Esto es lo generico
------------------------------------------------------------------

    def send_query() -> None:
        "Realiza una petición genérica"

        st.session_state.past.append(user_input)
        output = asyncio.run(st.session_state.api_helper.general_query(prepare_query(user_input)))
        st.session_state["input"] = ""
        st.session_state["generated"].append(output)


    _, col1, _ = st.colums([1,2,1])
    with col1:
        crear_boton_estandar("Envia Pregunta", key="b_pregunta", on_click=send_query)
"""

    comentario = """
-----------------------------------------------------------
RAG y gráfica
----------------------------------------------------------
"""

    # Manejo de la subida de documentos para el rag
    st.markdown("## File Upload for RAG")
    st.info("This widget allows you to upload files for use in Retrieval-Augmented Generation (RAG). Upload your document here to enhance the AI's knowledge base for more accurate responses.")

    uploaded_file = st.file_uploader("Suba un archivo", key="file_uploader", disabled=st.session_state.get("disabled", True))

    if uploaded_file is not None:
        # Recibimos los datos del servidor ftp y subimos el archivo
        ftp_client = FTPclient(*asyncio.run(st.session_state.api_helper.rag_query()))

        ftp_client.upload_file(
            uploaded_file
        )
    
    # Widget del gráfico de evaluaciones
    st.markdown("## Performance Graph [0-5]")
    st.info("This graph displays your performance metrics over time. It shows how your responses have been evaluated throughout the conversation.")

    if st.session_state.grade_array:
        # si se actualiza el array de valores, se actualiza la gráfica
        df = pd.DataFrame(st.session_state.grade_array)
        print(df)
        st.line_chart(df[1])
