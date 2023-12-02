import json 

class Usuario:
    def __init__(self, nombre, apellido, correo, contrasena,DNI): #Definimos la clase padre llama Usuario
      # Constructor de la clase Usuario que inicializa los atributos del usuario
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.contrasena = contrasena
        self.DNI = DNI

    def to_dict(self):
        # Método que devuelve un diccionario con los atributos del usuario
        return {
            "DNI": self.DNI,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "contrasena": self.contrasena
        }
        
    def olvidar_contrasena(self):
        # Aquí puedes implementar la lógica para restablecer la contraseña
        nueva_contrasena = input("Ingrese su nueva contraseña: ")
        self.contrasena = nueva_contrasena
        print("Contraseña restablecida exitosamente.")