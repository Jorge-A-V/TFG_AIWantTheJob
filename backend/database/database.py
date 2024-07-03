import sqlite3
import hashlib, base64
from typing import List, Any, Optional
import os

class DataBase:
    """
    Base de datos en texto plano basada en sqlite para guardar los datos de los usuarios.
    Esto incluye una tabla de usuario + contraseña y una tabla por usuario de valores de datos
    """
    def __init__(self) -> None:
        # Se conecta a la base de datos existente y si no la crea
        self.connection = sqlite3.connect('../backend/database/data/datos_usuarios.db', check_same_thread=False)

        # cursor para poder ejecutar las queries
        self.cursor = self.connection.cursor()

        # Creamos una base de datos de usuario y contraseña, la clave privada son ambos
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY,
                            username TEXT,
                            password TEXT,
                            salt TEXT,
                            identifier TEXT UNIQUE,
                            CONSTRAINT unique_username_password UNIQUE (username, password))''')

    def _generate_identifier(self, nombre: str, password: str) -> str:
        """
        Generamos el id en base al nombre y la contraseña, basicamente lo codificamos 
        a md5 y convertimos el hash a str para poder tratar con el

        Args
            - (string) nombre: nombre del usuario
            - (string) password: contraseña

        Returns 
            - (string) hash id
        """
        encoded_text = f"{nombre+password}".encode("utf-8")
        hash = hashlib.md5(encoded_text).digest(); 
        hash = base64.b64encode(hash).decode('utf-8'); 
        return self._f_hash(hash)
    
    def _f_hash(self, hash: str) -> str:
        """
        Añade comillas antes y despues del hash para evitar problemas al hacer los empaquetamientos/desepaquetamientos
        de mensajes

        Args
            - (string) hash
        
        Returns
            - (string) "hash"
        """
        hash_str =  "\""+hash+"\""
        hash_str = hash_str.replace("/", "") #unlucky edge case
        return hash_str


    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Hashea la contraseña y devuelve la contraseña y el hash
        """
        if salt is None:
            salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return base64.b64encode(password_hash).decode('utf-8'), base64.b64encode(salt).decode('utf-8')


    def registrar_usuario(self, nombre: str, password: str) -> str:
        """
        Intenta insertar un nuevo usuario dentro de la tabla users que tenemos en la base de datos.
        Si funciona creamos una tabla id que va a contener el progreso y devolvemos el id

        Args:
            - (string) nombre: nombre del usuario
            - (string) password: contraseña del usuario

        Returns
            - (string) hash id
        """            
        try:
            if not nombre or not password:
                return "Name probably registered or internal error"
            
            # Intentamos insertar los usuarios (miramos si existe ya)
            self.cursor.execute("SELECT username FROM users WHERE username = ?", (nombre,))
            if self.cursor.fetchone():
                return "Name probably registered or internal error"

            password_hash, salt = self._hash_password(password)
            u_id = self._generate_identifier(nombre, password)

            print(1)
            self.cursor.execute("INSERT INTO users (username, password, salt, identifier) VALUES (?, ?, ?, ?)", (nombre, password_hash, salt, u_id))

            print(1)
            # creamos la tabla de usario
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS {}
                  (id INTEGER PRIMARY KEY, value FLOAT)'''.format(u_id))
            
            print(1)
            # Inicializamos la tabla con un 0 (por cuestiones de estética)
            self.cursor.execute("INSERT INTO {} (value) VALUES (?)".format(u_id), (0, ))

            # Comiteamos y devolvemos el id
            self.connection.commit()
            return u_id
        except sqlite3.Error as e:
            # Rollback en caso de error
            self.connection.rollback()
            return "Name probably registered or internal error"

    def validar_usuario(self, nombre: str, password: str) -> str:
        """
        Intenta validar un usuario en la tabla de usuarios

        Args:
            - (string) nombre: nombre del usuario
            - (string) password: contraseña del usuario

        Returns
            - (string) hash id
        """
        try:
            # buscamos un usuario con el mismo nombre y verificamos que tenga la misma contraseña
            self.cursor.execute("SELECT password, salt, identifier FROM users WHERE username=?", (nombre,))
            recovered = self.cursor.fetchone()
            print(recovered)
            if not recovered:
                # error en el array pq no existe
                return "Error on validation"
            
            stored_password_hash, salt, identifier = recovered #cogemos la fila
        
            # la hasheamos y la comparamos con la antigua
            salt = base64.b64decode(salt)
            input_pass, _ = self._hash_password(password, salt)
            
            if input_pass == stored_password_hash:
                return identifier
            else:
                return "Error on validation"
        except Exception:
            return "Error on validation"

    def insertar_valor_array(self, identifier: str, value: int) -> List[Any]:
        """
        Intenta insertar un valor en la tabla de valores de un usuario ene concreto

        Args:
            - (string) identifier: id del usuario
            - (string) value: valor a insertar

        Returns
            - (List) Lista recuperada
        """
        try:
            if not isinstance(value, (int, float)):
                raise sqlite3.Error("Value must be a number")
            
            self.cursor.execute("INSERT INTO {} (value) VALUES (?)".format(identifier), (value, ))
            self.connection.commit()
        except sqlite3.Error as e:
            # Rollback en caso de error
            self.connection.rollback()
        #devolvemos los valores del usuario
        return self.recuperar_valores_array(identifier)
    
    def recuperar_valores_array(self, identifier: str) -> List[Any]:
        """
        Intenta recuperar el historial de valores de un usuario

        Args:
            - (string) identifier: id del usuario

        Returns
            - (List) Lista recuperada
        """
        try:
            self.cursor.execute("SELECT * FROM {} ".format(identifier))
            array = self.cursor.fetchall()
        except sqlite3.Error as e:
            array = [(0, 0.0)] # tupla con indice
        return array

    def close(self) -> None:
        """
        Cierra la conexión
        """
        self.connection.close()
