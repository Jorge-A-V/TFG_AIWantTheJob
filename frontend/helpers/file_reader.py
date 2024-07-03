from io import BytesIO

class FileReader:
    """
    Clase estática que lee un fichero y lo transforma a BytesIO
    """
    @staticmethod
    def read(file) -> BytesIO:
        """
        Función de leer fichero -> fichero en binario

        Args:
            - fichero abierto
        """
        bytes = file.read()
        file_obj = BytesIO(bytes)
        return file_obj