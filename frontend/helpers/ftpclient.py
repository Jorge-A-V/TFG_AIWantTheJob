import ftplib
from frontend.helpers.file_reader import FileReader

class FTPclient:
    """
    Clase cliente ftp. Sirve para instanciar un cliente ftp y subir un archivo.

    Args:
        - (string) address: dirección del servidor ftp
        - (string) port: puerto que tiene escuchando el servidor ftp
        - (string) user: credencial usuario con el que se hace el login
        - (string) password: credencial contraseña con el que se hace el login
    """
    def __init__(self, address: str, port: str, user: str, password: str) -> None:
        """
        Funcion init, rellena los parametros como propiedades e inicia la propiedad ftp (cliente ftp)
        """
        self.address = address  
        self.port = port
        self.user = user
        self.password = password
        self.ftp = ftplib.FTP()
        self._start()

    def _start(self) -> None:
        """
        Funcion de inicio privada, nos conectamos al servidor ftp y realizamos el login con los credenciales que tenemos
        """
        self.ftp.connect(self.address, self.port)
        self.ftp.login(self.user, self.password)

    def upload_file(self, file) -> None:
        """
        Funcion de subir ficheros al servidor ftp, solamente se puede subir ficheros no hay permisos para más. El fichero debe de estar
        abierto, son metadatos no un path. Inmediatamente después de subir el fichero, se cierra la conexión y se borra la instancia (es de un solo uso)
        """
        file_obj = FileReader.read(file)  #recibimos el fichero en binario
        with file_obj as f:
            self.ftp.storbinary(f'STOR {file.name}', f)
        
        self._close()

    def _close(self) -> None:
        """
        Función privada, cierra la conexión y borra la instancia
        """
        self.ftp.quit()
        del self
    