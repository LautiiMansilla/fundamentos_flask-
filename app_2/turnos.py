from flask import Flask, render_template,request
import json
from usuarios import Usuario
from flask import session,jsonify
from datetime import datetime, timedelta
from flask_mail import Mail,Message

class Paciente(Usuario):
    
    def __init__(self,nombre, apellido, correo, contrasena, DNI, obra_social, afiliado):
        super().__init__(nombre, apellido, correo, contrasena, DNI)
        self.obra_social = obra_social
        self.afiliado = afiliado
        self.turnos = []

    def agregar_turno(self, turno):
        self.turnos.append(turno)

    def to_dict(self): #Elegimos el formato con el cual queremos que se guarde en el json
        usuario_dict = super().to_dict() #Llamamos a la clase padre
        usuario_dict.update({
            "tipo": "paciente",
            "obra_social": self.obra_social,
            "afiliado": self.afiliado,
            "turnos": [turno.to_dict() for turno in self.turnos]
        })
        return usuario_dict

class Administrativo(Usuario):
    def __init__(self, nombre, apellido, correo, contrasena, sector,DNI):
        super().__init__(nombre, apellido, correo, contrasena,DNI)
        self.sector = sector

    def to_dict(self):
        usuario_dict = super().to_dict()
        usuario_dict.update({
            "tipo": "admin",
            "sector": self.sector
        })
        return usuario_dict

class Medico(Usuario):
    def __init__(self, nombre, apellido, DNI,correo, contrasena, especialidad):
        super().__init__(nombre, apellido,DNI, correo, contrasena)
        self.especialidad = especialidad

    def to_dict(self):
        usuario_dict = super().to_dict()
        usuario_dict.update({
            "tipo": "medico",
            "especialidad": self.especialidad
        })
        return usuario_dict

class Turno:
    def __init__(self, fecha, hora, motivo):
        self.motivo = motivo
        self.fecha = fecha
        self.hora = hora
        
    def to_dict(self):
        return {
            "motivo": self.motivo,
            "fecha": self.fecha,
            "hora": self.hora
        }

def registrar_paciente(paciente, filename="usuarios.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(paciente.to_dict())

    with open(filename, "w") as file:
        json.dump(data, file, indent=2)
        
def registrar_medico(medico, filename="usuarios_medico.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(medico.to_dict())

    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

def registrar_paciente_con_turnos(paciente, turnos, filename="usuarios.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    paciente_dict = paciente.to_dict()
    paciente_dict["turnos"] = [turno.to_dict() for turno in turnos]
    data.append(paciente_dict)

    with open(filename, "w") as file:
        json.dump(data, file, indent=2) 
        
def cargar_usuarios_desde_json(filename="usuarios.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)

        usuarios = []
        for usuario_data in data:
            tipo_usuario = usuario_data.get("tipo", None)

            if tipo_usuario == "paciente":
                usuario = cargar_paciente(usuario_data)
            elif tipo_usuario == "administrativo":
                usuario = cargar_administrativo(usuario_data)
            elif tipo_usuario == "medico":
                usuario = cargar_medico(usuario_data)
            else:
                # Manejar tipos de usuario desconocidos o no especificados
                continue

            usuarios.append(usuario)

        return usuarios
    except FileNotFoundError:
        print(f"El archivo {filename} no fue encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"Error al decodificar el archivo JSON: {filename}")
        return []

def guardar_datos_en_json(data, filename="usuarios.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

def cargar_usuarios_medicos_desde_json(filename="usuarios_medico.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)

        medicos = []
        for usuario_data in data:
            tipo_usuario = usuario_data.get("tipo", None)

            if tipo_usuario == "medico":
                medico = (usuario_data["DNI"], usuario_data["contrasena"])
                medicos.append(medico)

        return medicos
    except FileNotFoundError:
        print(f"El archivo {filename} no fue encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"Error al decodificar el archivo JSON: {filename}")
        return []

def cargar_usuarios_admin_desde_json(filename="usuarios_admin.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)

        administrativos = []
        for usuario_data in data:
            tipo_usuario = usuario_data.get("tipo", None)

            if tipo_usuario == "admin":
                admin = (usuario_data["correo"], usuario_data["contrasena"])
                administrativos.append(admin)

        return administrativos
    except FileNotFoundError:
        print(f"El archivo {filename} no fue encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"Error al decodificar el archivo JSON: {filename}")
        return []

def cargar_paciente(data):
    paciente = Paciente(
        data["nombre"],
        data["apellido"],
        data["correo"],
        data["contrasena"],
        data["DNI"],
        data["obra_social"],
        data["afiliado"]
    )
    for turno_data in data.get("turnos", []):
        turno = Turno(
            fecha=turno_data["fecha"],
            hora=turno_data["hora"],
            motivo=turno_data["motivo"]
        )
        paciente.agregar_turno(turno)
    return paciente

def cargar_administrativo(data):
    return Administrativo(
        data["nombre"],
        data["apellido"],
        data["correo"],
        data["DNI"],
        data["contrasena"],
        data["sector"]
    )

def cargar_medico(data):
    return Medico(
        data["nombre"],
        data["apellido"],
        data["DNI"],
        data["correo"],
        data["contrasena"],
        data["especialidad"]
    )

def iniciar_sesion(DNI, contrasena):
    usuarios = cargar_usuarios_desde_json()
    for usuario_data in usuarios:
        if usuario_data.DNI == DNI and usuario_data.contrasena == contrasena:
            return usuario_data
    return None

def iniciar_sesion_medico(DNI, contrasena):
    usuarios = cargar_usuarios_medicos_desde_json()
    for usuario_data in usuarios:
        if usuario_data[0] == DNI and usuario_data[1] == contrasena:
            return usuario_data
    return None

def iniciar_sesion_admin(correo, contrasena):
    usuarios = cargar_usuarios_admin_desde_json()
    for usuario_data in usuarios:
        if usuario_data[0] == correo and usuario_data[1] == contrasena:
            return usuario_data
    return None

def obtener_turnos_del_paciente(dni_paciente, filename="usuarios.json"):
    usuarios = cargar_usuarios_desde_json(filename)

    for usuario_data in usuarios:
        if usuario_data["DNI"] == dni_paciente and usuario_data.get("tipo") == "paciente":
            if "turnos" in usuario_data:
                # Si hay una clave 'turnos', significa que es un paciente con turnos
                turnos = []
                for turno_data in usuario_data["turnos"]:
                    turno = Turno(
                        fecha=turno_data["fecha"],
                        hora=turno_data["hora"],
                        motivo=turno_data["motivo"]
                    )
                    turnos.append(turno)
                return turnos

    return []  # Devolver una lista vacía si el paciente no se encuentra

def obtener_dni_del_usuario_actual():
    # Asumiendo que has almacenado el DNI del usuario en la sesión durante el proceso de inicio de sesión
    return session.get('dni_usuario_actual', None)

def agregar_turno(fecha, hora, motivo, filename="usuarios.json"):
    dni_paciente = session.get('dni_usuario_actual')

    if dni_paciente:
        # Cargar todos los usuarios desde el archivo JSON
        usuarios = cargar_usuarios_desde_json(filename)

        # Buscar al paciente actual en la lista de usuarios
        paciente = next((usuario for usuario in usuarios if usuario.get("DNI") == dni_paciente and usuario.get("tipo") == "paciente"), None)

        # Verificar que el paciente y el nuevo_turno no sean None antes de intentar agregar el turno
        if paciente is not None:
            nuevo_turno = Turno(fecha=fecha, hora=hora, motivo=motivo)
            if nuevo_turno is not None:
                # Agregar el nuevo turno a la lista de turnos del paciente
                paciente["turnos"] = paciente.get("turnos", []) + [nuevo_turno.to_dict()]

                # Impresiones de depuración
                print("DEBUG: Paciente antes de guardar en JSON:", paciente)
                print("DEBUG: Usuarios antes de guardar en JSON:", usuarios)

                # Guardar todos los usuarios actualizados en el archivo JSON
                guardar_datos_en_json(usuarios, filename)

                # Impresiones de depuración
                print("DEBUG: Usuarios después de guardar en JSON:", usuarios)

                return True

    return False

def obtener_nombre_del_usuario_actual(dni):
    # Asumiendo que has almacenado el DNI del usuario en la sesión durante el proceso de inicio de sesión
    dni_usuario = dni

    if dni_usuario is not None:
        # Cargar datos desde el JSON
        with open("usuarios.json", "r") as file:
            data = json.load(file)

        # Buscar el usuario en el JSON
        for usuario_data in data:
            if usuario_data.get("DNI") == dni_usuario:
                # Devolver el nombre del usuario
                return usuario_data.get("nombre")

    return None  # Devolver None si el DNI no se encuentra en el JSON

def obtener_apellido_del_usuario_actual(dni):
    # Asumiendo que has almacenado el DNI del usuario en la sesión durante el proceso de inicio de sesión
    dni_usuario = dni

    if dni_usuario is not None:
        # Cargar datos desde el JSON
        with open("usuarios.json", "r") as file:
            data = json.load(file)

        # Buscar el usuario en el JSON
        for usuario_data in data:
            if usuario_data.get("DNI") == dni_usuario:
                # Devolver el nombre del usuario
                return usuario_data.get("apellido")

    return None  # Devolver None si el DNI no se encuentra en el JSON

def obtener_mail_del_usuario_actual(dni):
    # Asumiendo que has almacenado el DNI del usuario en la sesión durante el proceso de inicio de sesión
    dni_usuario = dni
    if dni_usuario is not None:
        # Cargar datos desde el JSON
        with open("usuarios.json", "r") as file:
            data = json.load(file)

        # Buscar el usuario en el JSON
        for usuario_data in data:
            if usuario_data.get("DNI") == dni_usuario:
                # Devolver el nombre del usuario
                return usuario_data.get("correo")

    return None  # Devolver None si el DNI no se encuentra en el JSON

def obtener_obra_social_del_usuario_actual(dni):
        # Asumiendo que has almacenado el número de obra social del usuario en la sesión durante el proceso de inicio de sesión
    dni_usuario = dni
    if dni_usuario is not None:
        # Cargar datos desde el JSON
        with open("usuarios.json", "r") as file:
            data = json.load(file)

        # Buscar el usuario en el JSON
        for usuario_data in data:
            if usuario_data.get("DNI") == dni_usuario:
                # Devolver el nombre del usuario
                return usuario_data.get("obra_social")

    return None  # Devolver None si el DNI no se encuentra en el JSON

def obtener_afiliado_del_usuario_actual(dni):
        # Asumiendo que has almacenado el número de obra social del usuario en la sesión durante el proceso de inicio de sesión
    dni_usuario = dni
    if dni_usuario is not None:
        # Cargar datos desde el JSON
        with open("usuarios.json", "r") as file:
            data = json.load(file)

        # Buscar el usuario en el JSON
        for usuario_data in data:
            if usuario_data.get("DNI") == dni_usuario:
                # Devolver el nombre del usuario
                return usuario_data.get("afiliado")

    return None  # Devolver None si el DNI no se encuentra en el JSON

def obtener_horas_disponibles():
    horas_disponibles =["08:30", "09:00", "09:30", "10:00", "10:30", "11:00","11:30", "12:00", "12:30", "13:00", "13:30", "14:00","14:30", "15:00", "15:30", "16:00", "16:30", "17:00","17:30", "18:00"]
    return horas_disponibles
    
def obtener_motivos_disponibles():
    motivos_disponibles = ["CARDIOLOGIA","CLINICA MEDICA", "DERMATOLOGIA", "GASTROENTEROLOGIA","GINECOLOGIA","MAMOGRAFIA","NEUMONOLOGIGA","NEUROLOGIA","NUTRICION Y DIABETOLOGIA","OBSTETRICIA","OFTALMOLOGIA","ONCOLOGIA","OTORRINONARINGOLOGIA","PEDIATRIA","TRAUMATOLOGIA Y ORTOPEDIA","UROLOGIA"]
    return motivos_disponibles

def guardar_turno_en_json(dni, turno, filename="usuarios.json"):
    # Cargar datos existentes de los usuarios desde el archivo JSON
    try:
        with open(filename, 'r') as file:
            usuarios = json.load(file)
    except FileNotFoundError:
        # Si el archivo no existe, inicializar datos de los usuarios
        usuarios = []

    # Buscar el usuario por DNI y agregar el nuevo turno a la lista de turnos
    for usuario_data in usuarios:
        if usuario_data.get("DNI") == dni:
            if "turnos" not in usuario_data:
                usuario_data["turnos"] = []
            usuario_data["turnos"].append(turno)
            break

    # Guardar los datos actualizados en el archivo JSON
    with open(filename, 'w') as file:
        json.dump(usuarios, file, indent=4)

def obtener_datos_usuario_actual():
    if 'dni_usuario_actual' in session:
        return str(session['dni_usuario_actual'])
    return None

def enviar_correo(paciente, turno):
    app = Flask(__name__)

    # Configuración de Flask-Mail para Gmail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587  # El puerto para TLS
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'hospital.buencorazon@gmail.com'  # Tu dirección de correo de Gmail
    app.config['MAIL_PASSWORD'] = 'sgfw vdkr khhv slcb'  # La contraseña de tu cuenta de Gmail o la contraseña de aplicación generada

    mail = Mail(app)    

    # Configurar el mensaje
    mensaje = Message(subject='Confirmación de Turno',
                      sender='hospital.buencorazon@gmail.com',
                      recipients=[paciente.correo])

    # Contenido del correo (puedes usar HTML también)
    mensaje.body = f'Tu turno para el {turno.fecha} a las {turno.hora} ha sido agendado correctamente.'

    try:
        # Enviar el correo
        with app.app_context():
            mail.send(mensaje)
        print("DEBUG: Correo enviado correctamente")
    except Exception as e:
        print(f"DEBUG: Error al enviar el correo: {str(e)}")