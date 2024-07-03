#https://github.com/AI-Yash/st-chat/blob/main/examples/chatbot.py

import streamlit as st
from streamlit_chat import message
import requests
from requests.adapters import HTTPAdapter

st.set_page_config(
    page_title="Streamlit Chat - Demo",
    page_icon=":robot:"
)

#API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
#headers = {"Authorization": st.secrets['api_key']}


st.header("Streamlit Chat - Demo")
st.markdown("[Github](https://github.com/ai-yash/st-chat)")

if 'bot_1' not in st.session_state:
    st.session_state.disabled = False

def disable_enable():
    status = st.session_state.get("disabled", True)
    if status:
        st.session_state["disabled"] = False
    else:
        st.session_state["disabled"] = True

st.button("Click", key="bot_1", on_click=disable_enable, disabled=st.session_state.get("disabled", True))
 
st.button("Click", key="bot_2", on_click=disable_enable, disabled=not st.session_state.get("disabled", True))


st.file_uploader("Suba un archivpo")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

notDone = True
def query(payload):
    return "prueba"

def get_text():
    input_text = st.text_input(label="Chat", key="input", disabled=st.session_state.get("disabled", True))
    return input_text 


user_input = get_text()

if user_input:
    print(1)
    #output = query({
     #   "inputs": {
      #      "past_user_inputs": st.session_state.past,
       #     "generated_responses": st.session_state.generated,
        #    "text": user_input,
        #},"parameters": {"repetition_penalty": 1.33},
    #})

    st.session_state.past.append(user_input)

    try:
        json =             {
                "pregunta": user_input,
            }
        output = query(
            json
        )
        st.session_state.generated.append(output["respuesta"])
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the server.")
    print(2)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
