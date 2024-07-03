class NumberGrabber:
    """
    Parsea un texto en concreto para obtener el primer numero. Esta pensado para ser combinado 
    con el texto de evaluación del modelo
    """
    def __init__(self) -> None:
        pass

    def grab_number(self, text: str) -> int:
        """
        Devuelve el primer numero que se encuentra en el texto

        Args
            - (string) text: texto a parsear
        
        Returns
            - (int) el valor encontrado o 0 si no encuentra nada
        """
        for character in text.split():
            if character.isdigit():
                return int(character)
        return 0