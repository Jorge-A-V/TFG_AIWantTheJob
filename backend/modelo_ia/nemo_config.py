import os

class NemoConfig:
    """
    Clase que simplifica la interfaz de acceso a las configuraciones, permite ademas crear de manera
    automática las YAML config (que son las que varian)

    Args:
        - (sting) model_name: nombre del modelo (repo de hugging)
    """
    def __init__(self, model_name: str) -> None:
        self.COLANG_CONFIG = self._set_colang_config("hardcoded_colang.co") # NAIVE COLANG AQUI PARA CAMBIAR DE CONFIG
        self.YAML_CONFIG = self._set_yaml_config(model_name) # actualiza la nomenclatura del yaml

    def _set_colang_config(self, filename: str = None) -> str:
        """
        Lee la configuración Colang desde el archivo.

        Args
            - (string) nombre del archivo

        Returns:
            - (string) configuración Colang
        """
        # nos ponemos en el fichero modelo_ia y vamos hacia las config
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, f'nemo_config_files/{filename}')
        with open(config_path, 'r') as file:
            return file.read()

    def _set_yaml_config(self, model_name: str) -> str:
        """
        Funcion privada, devuelve la YAML_CONFIG creada y crea el engine de la instancia a partir
        del model_name

        Args:
            - (sting) model_name: nombre del modelo (repo de hugging)

        Returns
            - (string) yaml config
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'nemo_config_files/yaml_config.yaml')
        with open(config_path, 'r') as file:
            config_text = file.read()

        config = config_text.replace("{path}", model_name)
        self.engine = "hf_engine_" + model_name[model_name.index("/")+1:]
        config = config.replace("{engine}", self.engine)

        return config
