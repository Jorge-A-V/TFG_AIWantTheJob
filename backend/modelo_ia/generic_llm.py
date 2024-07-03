from transformers import AutoTokenizer, GenerationConfig, pipeline
from langchain import PromptTemplate
from langchain.chains import LLMChain
import torch
from torch import cuda
from torch import cuda, bfloat16
import transformers
from nemoguardrails.llm.providers import(
    HuggingFacePipelineCompatible,
)

from typing import Literal, List, DefaultDict

from backend.modelo_ia.prompt_templates import PromptTemplates

class LLM:
    """
    Clase interna que encapsula nuestro modelo. Instancia tanto modelo como railes de seguridad.

    Args:
        - (string) model_name: nombre del modelo que queremos utilizar (necesita compatibilidad con HuggigFace)
        - (literal) loading_model: cuantification del modelo (si se quiere) - defaults @ 4bit
    """
    def __init__(self, 
                 model_name: str = "meta-llama/Llama-2-7b-chat-hf", 
                 loading_mode: Literal["4bit","8bit"] = "4bit"
                 ) -> None:
        
        # callback internos
        self.question_response = None
        self.rag_question_response = None
        self.emulate_answer = None
        self.punctuate_answer = None

        # Chain de langchain
        self.llm = None

        self._model_start(model_name=model_name, loading_mode=loading_mode)

    """
    ---------------------------------------------------------------------------
    FUCION QUE INICIA EL MODELO
    ---------------------------------------------------------------------------
    """

    def _model_start(self, 
                     model_name: str, 
                     loading_mode = None) -> None:
        """
        Función privada que inicia el modelo a través de langchain.

        Args:
            - (string) model_name: nombre del repositorio de hugging o path local al modelo
            - (literal) loading_model: cuantification si se quiere
        """
        #MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"

        device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'
        
        bnb_config = None
        #Cuantizamos manualmente el modelo (solo si el cuda esta disponible)
        if cuda.is_available():
            print(loading_mode, loading_mode == "4bit")
            if loading_mode == "4bit":
                print("EL MODELO ES 4bit")
                bnb_config = transformers.BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type='nf4',
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=bfloat16
                )
            if loading_mode == "8bit":
                bnb_config = transformers.BitsAndBytesConfig(
                    load_in_8bit=True,
                )
        cuant_config = {"quantization_config": bnb_config} if bnb_config is not None else {}

        model_config = transformers.AutoConfig.from_pretrained(
            model_name
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        
        if loading_mode == "No cuant": # pa los tests fp16 es menos cuantizacion
            model = transformers.AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=torch.float16, trust_remote_code=True, device_map="auto"
            )
        else:
            #Lo instanciamos
            model = transformers.AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                config=model_config,
                device_map='auto',
                **cuant_config
            )

        generation_config = GenerationConfig.from_pretrained(model_name)
        generation_config.max_new_tokens = 400
        generation_config.temperature = 1.25
        generation_config.top_p = 0.95
        generation_config.do_sample = True
        generation_config.repetition_penalty = 1.25
        
        #Creamos una pipeline de texto
        text_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            generation_config=generation_config,
        )
        
        #Hacemos un wrapper para poder usar Nemo
        llm = HuggingFacePipelineCompatible(pipeline=text_pipeline)
        
        #Hacemos un pipeline para los callbacks (a ver si asi me evito tener 2 instancias en memoria)
        self.llm = llm

        self._set_default_callbacks()

    """
    ---------------------------------------------------------------------------
    FUCION PARA CREAR LOS CALLBACKS
    ---------------------------------------------------------------------------
    """

    def _set_default_callbacks(self):
        # Cargamos las preguntas en base a los prompt-templates que tenemos en PromptTemplates
        self.question_response = self._set_callback(PromptTemplates.question_sysprompt_template)
        self.emulate_answer = self._set_callback(PromptTemplates.give_example_output_sysprompt_template)
        self.punctuate_answer = self._set_callback(PromptTemplates.punctuate_answer_sysprompt_template)
        # Para el naive
        # self.summarize = self._set_callback("Please summarize the topic of the following text")

    def _set_callback(self, 
                        sysprompt: str = "Act as an interviewer in the midst of an interview",
                        template: str = PromptTemplates.phi1template
        ) -> None:
        """
        Funcion que crea en el modelo la función interna para procesar llamadas/queries  de crear preguntas.
        Basicamente creamos una función <responder> que metemos en la clase -> self.responder, para poder luego
        meter como callback en el Nemo

        Args:
            - (sysprompt) prompt de systema, por defecto invoca a chat_template si tiene, si no se tira por template
            - (formatted string): template, template para la pregunta. (Si se quiere sysprompt, meter el sysprompt tambien
            como argumento)
        """
        
        messages = [
            {"role": "system", "content": sysprompt},
            {"role": "user", "content": "{text}"}
        ]

        if self.tokenizer.chat_template is not None:
            template = self._get_chat_template(messages)
        else:
            template = template.replace("{sys_p}", sysprompt)

        # Creamos la promptemplate indicando que se va a sustituir
        prompt = PromptTemplate(
            input_variables=["text"],
            template=template,
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        #Creamos la llamada asincrona de la función y la guardamos como callback
        async def q_response(inputs: str):
            print(sysprompt, inputs)
            return chain.invoke(inputs)["text"]
        
        return q_response
    
    def _get_chat_template(self, messages: List[DefaultDict[str, str]]) -> str:
        """
        Sacamos la chat_template del tokenizer

        Args:
            - (list) messages: lista de diccionarios con mensajes

        Returns
            - (str) template
        """
        try:
            template = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            messages[1]["content"] = messages[0]["content"] + "\n" + messages[1]["content"]
            template = self.tokenizer.apply_chat_template(
                messages[1:], #Si llegamos aqui es porque no tiene sysprompt el template entonces no lo cogemos
                tokenize=False,
                add_generation_prompt=True,
            )
        return template



