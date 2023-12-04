from flask import Flask, render_template, request, redirect, url_for,jsonify
import json
from turnos import Paciente, registrar_paciente,Medico,Administrativo
from turnos import Turno
from datetime import datetime
from turnos import  Paciente, obtener_turnos_del_paciente, obtener_dni_del_usuario_actual, agregar_turno, obtener_horas_disponibles, obtener_motivos_disponibles, cargar_usuarios_desde_json
from flask import flash,session
from turnos import iniciar_sesion, guardar_turno_en_json,obtener_nombre_del_usuario_actual,obtener_obra_social_del_usuario_actual, agregar_turno,cargar_usuarios_medicos_desde_json,registrar_medico,buscar_usuario_por_correo,generar_token,enviar_correo_olvido_contrasena
from turnos import iniciar_sesion_admin,obtener_apellido_del_usuario_actual,iniciar_sesion_medico,obtener_afiliado_del_usuario_actual, enviar_correo,obtener_mail_del_usuario_actual,es_contrasena_segura,guardar_datos_en_json,validar_token
from flask_mail import Mail

# se crea una aplicacion web flask
app = Flask(__name__)
app.secret_key = "NXeKZNWIfpJmaLo"
dni_usuario_actual = None

# estructura de datos para almacenar detalles de turnos
datos_turno = {
    'motivo': None,
    'fecha': None,
    'hora': None
}

# define una ruta para la página de inicio
@app.route('/hospital_buen_corazon')
def index():
    return render_template("index.html")

# define una ruta para el menu de pacientes
@app.route('/menu_paciente')
def menu_paciente():
    return render_template('menu_paciente.html')

#LISTA DE PACIENTES QUE VA A VER EL ADMINISTRATIVO
@app.route('/lista_pacientes_admin')
def lista_de_pacientes():
    # carga los datos de usuario desde un archivo JSON
    with open('usuarios.json') as file:
        data = json.load(file)
    return render_template("lista_de_pacientes.html", usuarios=data)

#MIS DATOS PACIENTE
@app.route('/mis_datos_p')
def mis_datos():
    # Obtén el DNI del usuario actual desde la sesión
    dni_usuario_actual = session.get('dni_usuario_actual')

    # Carga los datos de usuario desde un archivo JSON
    with open('usuarios.json') as file:
        data = json.load(file)

    # Busca al usuario actual en la lista de usuarios
    usuario_actual = next((usuario for usuario in data if usuario.get('DNI') == dni_usuario_actual), None)

    # Obtén los turnos del usuario actual si es un paciente
    turnos = usuario_actual.get('turnos', []) if usuario_actual and usuario_actual.get('tipo') == 'paciente' else []

    return render_template("mis_datos_p.html", turnos=turnos, obra_social_usuario=obra_social_usuario,mail_usuario_actual=mail_usuario_actual, afiliado_usuario_actual=afiliado_usuario_actual)

@app.route('/lista_medico')
def lista_medico():
    # carga los datos de usuario desde un archivo JSON
    with open('usuarios_medico.json') as file:
        data = json.load(file)
    return render_template("lista_medico.html", usuarios=data)

# define una ruta para mostrar las especialidades médicas
@app.route('/especialidades')
def especialidades():
    especialidades=obtener_motivos_disponibles()
    # carga los datos de usuario desde un archivo JSON
    with open('usuarios.json') as file:
        data = json.load(file)
    return render_template("especialidades.html",usuarios=data,especialidades=especialidades)

#LISTA PACIENTES
@app.route('/lista_pacientes')
def lista_pacientes():
    # carga los datos de usuario desde un archivo JSON
    with open('usuarios.json') as file:
        data = json.load(file)
    return render_template("lista_pacientes.html", usuarios=data)

@app.route('/mis_turnos')
def mis_turnos():
    # Obtén el DNI del usuario actual desde la sesión
    dni_usuario_actual = session.get('dni_usuario_actual')

    # Carga los datos de usuario desde un archivo JSON
    with open('usuarios.json') as file:
        data = json.load(file)

    # Busca al usuario actual en la lista de usuarios
    usuario_actual = next((usuario for usuario in data if usuario.get('DNI') == dni_usuario_actual), None)

    # Obtén los turnos del usuario actual si es un paciente
    turnos = usuario_actual.get('turnos', []) if usuario_actual and usuario_actual.get('tipo') == 'paciente' else []

    return render_template("mis_turnos.html", turnos=turnos)

@app.context_processor
def inject_user():
    dni_usuario_actual = session.get('dni_usuario_actual')
    nombre_usuario_actual = obtener_nombre_del_usuario_actual(dni_usuario_actual)
    apellido_usuario_actual= obtener_apellido_del_usuario_actual(dni_usuario_actual)

    # Devuelve un diccionario con las variables que quieres que estén disponibles en los contextos
    return dict(dni_usuario_actual=dni_usuario_actual, nombre_usuario_actual=nombre_usuario_actual,apellido_usuario_actual=apellido_usuario_actual)

#RENDER DE LA PAGINA PRINCIPAL PACIENTE PARA USAR BOTONES DE MANERA MAS COMODA.
@app.route('/paciente')
def paciente():
    global dni_usuario_actual
    global nombre_usuario_actual
    global apellido_usuario_actual
    global obra_social_usuario
    global afiliado_usuario_actual
    global mail_usuario_actual

    if 'dni_usuario_actual' in session:
        dni = session['dni_usuario_actual']
        # Carga los datos de usuario desde un archivo JSON
        with open('usuarios.json') as file:
            data = json.load(file)

        # Busca al usuario actual en la lista de usuarios
        usuario_actual = next((usuario for usuario in data if usuario.get('DNI') == dni), None)

        if usuario_actual:
            nombre_usuario_actual = usuario_actual.get('nombre')
            obra_social_usuario = usuario_actual.get('obra_social')
            apellido_usuario_actual = usuario_actual.get('apellido')
            afiliado_usuario_actual = usuario_actual.get('afiliado')
            mail_usuario_actual = usuario_actual.get('correo')

            return render_template("paciente.html", dni_usuario_actual=dni, nombre_usuario_actual=nombre_usuario_actual, obra_social_usuario=obra_social_usuario, apellido_usuario_actual=apellido_usuario_actual)
        else:
            return render_template('error.html', mensaje="Usuario no encontrado en el archivo JSON")
    else:
        return render_template('error.html', mensaje="Usuario no ha iniciado sesión")
    
    
@app.route('/iniciar_sesion_p', methods=['GET', 'POST'])
# Función para iniciar sesión en la página
def iniciar_sesion_pagina():
    global dni_usuario_actual
    global nombre_usuario_actual
    global apellido_usuario_actual
    global obra_social_usuario
    global afiliado_usuario_actual
    global mail_usuario_actual

    if request.method == 'POST':
        dni = request.form['dni']
        password = request.form['password']
        # intenta iniciar sesión del usuario
        usuario = iniciar_sesion(dni, password)
        if usuario is not None:
            session['dni_usuario_actual'] = str(dni)
            dni_usuario_actual = dni
            # Pasa el DNI como argumento para obtener el nombre del usuario
            nombre_usuario_actual = obtener_nombre_del_usuario_actual(dni)
            print(f"DEBUG: {nombre_usuario_actual}")
            obra_social_usuario = obtener_obra_social_del_usuario_actual(dni)
            print(f"DEBUG: {obra_social_usuario}")
            apellido_usuario_actual=obtener_apellido_del_usuario_actual(dni)
            print(f"DEBUG: {apellido_usuario_actual}")
            afiliado_usuario_actual= obtener_afiliado_del_usuario_actual(dni)
            print(f"DEBUG: {afiliado_usuario_actual}")
            mail_usuario_actual= obtener_mail_del_usuario_actual(dni)
            print(f"DEBUG: { mail_usuario_actual}")

            # Renderiza la página del paciente con la información del usuario
            return render_template("paciente.html", dni_usuario_actual=dni, nombre_usuario_actual=nombre_usuario_actual, obra_social_usuario=obra_social_usuario,apellido_usuario_actual=apellido_usuario_actual)
        else:
            # Renderiza una página de error para credenciales incorrectas
            return render_template('error.html', mensaje="Credenciales incorrectas - Verifica usuario y contraseña - Verifica tipo de usuario")
    return render_template('iniciar_sesion_p.html')

@app.route('/lista_turnos')
def lista_turnos():
    with open('usuarios.json') as file:
            data = json.load(file)
    return render_template("lista_turnos.html",usuarios=data)        
          
# Define una ruta y función para iniciar sesión de profesionales médicos
@app.route('/iniciar_sesion_m', methods=['GET', 'POST'])
def iniciar_sesion_m():
    if request.method == 'POST':
        DNI = request.form['dni']
        password = request.form['password']       
        with open('usuarios.json') as file:
            data = json.load(file)
        # Intenta iniciar sesión del profesional médico
        usuario = iniciar_sesion_medico(DNI, password)
        if usuario is not None:
            session['dni_usuario_actual'] = str(DNI)
            # Renderiza la página del profesional médico tras un inicio de sesión exitoso
            return render_template("medico.html",usuarios=data,)
        else:
            # Renderiza una página de error para credenciales incorrectas
            return render_template('error.html', mensaje="Credenciales incorrectas - Verifica usuario y contraseña - Verifica tipo de usuario")
    return render_template('iniciar_sesion_m.html')

#INICIAR SESION ADMINISTRADOR
@app.route('/iniciar_sesion_admin', methods=['GET', 'POST'])
def iniciar_sesion_administrativo():
    if request.method == 'POST':
        mail = request.form['correo']
        password = request.form['password']
        with open('usuarios.json') as file:
            data = json.load(file)
         # Intenta iniciar sesión del profesional médico
        usuario = iniciar_sesion_admin(mail,password)
        if usuario is not None:
             # Renderiza la página del profesional médico tras un inicio de sesión exitoso
            return render_template("administrativo.html",usuarios=data)
        else:
            # Renderiza una página de error para credenciales incorrectas
            return render_template('error.html', mensaje="Credenciales incorrectas - Verifica usuario y contraseña - Verifica tipo de usuario")
    return render_template('iniciar_sesion_admin.html')

# Define una ruta y función para el registro de pacientes
@app.route('/registrar_p', methods=['GET', 'POST'])
def registrar_p():
    mensaje = None
    if request.method == 'POST':
        # Obtiene la entrada del usuario desde el formulario de registro
        nombre = request.form["nombre"]
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        dni = request.form['dni']
        obra_social = request.form['obra_social']
        afiliado = request.form['afiliado']

        # Verifica si la contraseña es segura
        if not es_contrasena_segura(password):
            mensaje = "La contraseña no cumple con los requisitos de seguridad. Minimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número  "
        else:
            # Carga los usuarios existentes desde un archivo JSON
            usuarios = cargar_usuarios_desde_json("usuarios.json")

            # Verifica si ya existe un usuario con el mismo DNI
            for usuario_data in usuarios:
                if isinstance(usuario_data, Paciente) and usuario_data.DNI == dni:
                    mensaje = "Ya existe un usuario con el mismo DNI. Por favor, ingrese otro DNI."

            # Si no se encuentra un DNI duplicado y la contraseña es segura, procede con el registro
            if mensaje is None:
                paciente = Paciente(nombre, apellido, email, password, dni, obra_social, afiliado)
                try:
                    registrar_paciente(paciente)
                    mensaje = "Registro exitoso. Ahora puede iniciar sesión."
                except Exception as e:
                    mensaje = f'Error al registrar al paciente: {str(e)}'

    # Renderiza la página de registro de pacientes con el mensaje apropiado
    return render_template("registrar_p.html", mensaje=mensaje)

# Define una ruta y función para el registro de profesionales médicos
@app.route('/registrar_medicos', methods=['GET', 'POST'])
def registrar_medicos():
    # Obtiene los motivos disponibles para agendar citas
    motivos_disponibles = obtener_motivos_disponibles()
    mensaje = None

    if request.method == 'POST':
        # Obtiene la entrada del usuario desde el formulario de registro
        dni = request.form['dni']
        nombre = request.form["nombre"]
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        especialidad = request.form['especialidad']

        # Carga los usuarios existentes desde un archivo JSON
        usuarios = cargar_usuarios_medicos_desde_json("usuarios_medico.json")

        # Verifica si ya existe un usuario con el mismo DNI
        for usuario_data in usuarios:
            if isinstance(usuario_data, Medico) and usuario_data.DNI == dni:
                mensaje = "Ya existe un usuario con el mismo DNI. Por favor, ingrese otro DNI."

        # Si no se encuentra un DNI duplicado, procede con el registro
        if mensaje is None:
            medico = Medico(nombre, apellido, dni, email, password, especialidad)
            try:
                registrar_medico(medico, "usuarios_medico.json")
                mensaje = "Registro exitoso. Ahora puede iniciar sesión."
            except Exception as e:
                mensaje = f'Error al registrar al médico: {str(e)}'

    # Renderiza la página de registro de profesionales médicos con el mensaje apropiado
    return render_template("registrar_medicos.html", mensaje=mensaje, motivos_disponibles=motivos_disponibles)
# Define una ruta y función para agendar un turno

@app.route('/agendar_turnos', methods=['GET', 'POST'])
def agendar_turnos():
    # Cargar datos existentes desde el archivo JSON
    usuarios = cargar_usuarios_desde_json("usuarios.json")
    message = None

    if request.method == 'POST':
        fecha_turno = request.form.get('fecha')
        hora_turno = request.form.get('hora')
        motivo_turno = request.form.get('motivo')

        if not all([fecha_turno, hora_turno, motivo_turno]):
            message = "Todos los campos son obligatorios."
        else:
            dni_usuario_actual = obtener_dni_del_usuario_actual()

            if dni_usuario_actual is not None:
                paciente = next((usuario for usuario in usuarios if isinstance(usuario, Paciente) and usuario.DNI == dni_usuario_actual), None)

                if paciente is not None:
                    nuevo_turno = Turno(fecha=fecha_turno, hora=hora_turno, motivo=motivo_turno)

                    if nuevo_turno is not None:
                        try:
                            # Actualizar el turno del paciente
                            paciente.agregar_turno(nuevo_turno)

                            # Guardar la lista actualizada en el archivo JSON
                            with open("usuarios.json", "w") as file:
                                json.dump([usuario.to_dict() for usuario in usuarios], file, indent=2)

                            message = "Turno agendado correctamente"
                            enviar_correo(paciente, nuevo_turno)
                            print("DEBUG: Turno agendado correctamente")
                        except Exception as e:
                            message = f"Error al agendar el turno: {str(e)}"
                            print(f"DEBUG: Error al agendar el turno: {str(e)}")
                    else:
                        print("DEBUG: El nuevo turno no se creó correctamente.")
                else:
                    print(f"DEBUG: No se encontró al paciente con DNI {dni_usuario_actual}.")
            else:
                print("DEBUG: No se pudo obtener el DNI del usuario actual.")

    motivos_disponibles = obtener_motivos_disponibles()
    horas_disponibles = obtener_horas_disponibles()

    return render_template("agendar_turnos.html", message=message, motivos_disponibles=motivos_disponibles, horas_disponibles=horas_disponibles)

@app.route('/buscar_medico', methods=['POST'])
def buscar_medico():
    dni_busqueda = request.form.get('dni_busqueda')
    with open('usuarios_medico.json') as file:
        data = json.load(file)

    medico_encontrado = None
    for usuario in data:
        if usuario.get('tipo') == 'medico' and usuario.get('DNI') == dni_busqueda:
            medico_encontrado = usuario
            break

    return render_template('info_medico.html', medico_encontrado=medico_encontrado)

@app.route('/eliminar_medico', methods=['POST'])
def eliminar_medico():
    dni_eliminar = request.form.get('dni_eliminar')
    with open('usuarios_medico.json') as file:
        data = json.load(file)

    # Encuentra al médico en la lista y elimínalo
    for usuario in data:
        if usuario.get('tipo') == 'medico' and usuario.get('DNI') == dni_eliminar:
            data.remove(usuario)
            break

    # Guarda los datos actualizados en el archivo JSON
    with open('usuarios_medico.json', 'w') as file:
        json.dump(data, file, indent=2)

    return redirect(url_for('lista_medico'))

@app.route('/eliminar_turno', methods=['POST'])
def eliminar_turno():
    if request.method == 'POST':
        dni_paciente = request.form.get('dni_paciente')
        fecha_turno = request.form.get('fecha_turno')
        hora_turno = request.form.get('hora_turno')
        
        # Cargar usuarios desde el JSON
        cargar_usuarios_desde_json()

        with open('usuarios.json', 'r') as file:
            data = json.load(file)

        paciente_encontrado = None
        for usuario in data:
            if usuario.get('tipo') == 'paciente' and usuario.get('DNI') == dni_paciente:
                paciente_encontrado = usuario
                break

        if paciente_encontrado is not None:
            # Encuentra el turno en la lista de turnos del paciente y elimínalo
            turnos_paciente = paciente_encontrado.get('turnos', [])
            for turno in turnos_paciente:
                if turno.get('fecha') == fecha_turno and turno.get('hora') == hora_turno:
                    turnos_paciente.remove(turno)
                    break

            # Actualiza la lista de turnos del paciente en el archivo JSON
            with open('usuarios.json', 'w') as file:
                json.dump(data, file, indent=2)

            # Muestra un mensaje de éxito
            flash('El turno fue eliminado correctamente', 'success')

    # Recargar la misma página con el mensaje flash y los usuarios actualizados
    with open('usuarios.json') as file:
        data = json.load(file)
    return render_template("lista_turnos.html", usuarios=data)

@app.route('/olvido_contrasena', methods=['GET', 'POST'])
def olvido_contrasena():
    if request.method == 'POST':
        correo = request.form.get('correo')
        usuario = buscar_usuario_por_correo(correo)
        if usuario:
            token = generar_token(usuario)
            # Redirigir a la página 'ingresar_token' y proporcionar correo y token como argumentos
            return redirect(url_for('ingresar_token', correo=correo, token=token))
        else:
            # Informar al usuario que el correo no está registrado
            return render_template('error.html')
    return render_template('ingresar_mail.html')

@app.route('/ingresar_token/<correo>/<token>', methods=['GET', 'POST'])
def ingresar_token(correo, token):
    if request.method == 'POST':
        token = request.form['token']

        usuarios = cargar_usuarios_desde_json()
        usuario = buscar_usuario_por_correo(correo)

        if usuario and usuario['token'] == token:
            # Token válido, redirige al usuario a restablecer la contraseña
            return redirect(url_for('restablecer_contrasena', token=token))
        else:
            # Token no válido, muestra un mensaje de error
            return render_template('error.html')

    return render_template('ingresar_token.html')

@app.route('/restablecer_contrasena', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    # Validar el token
    usuario = validar_token(token)
    if usuario:
        if request.method == 'POST':
            nueva_contrasena = request.form.get('nueva_contrasena')
            # Actualizar la contraseña del usuario
            usuario['contrasena'] = nueva_contrasena
            # Almacenar el usuario actualizado en el archivo JSON
            usuarios = cargar_usuarios_desde_json("usuarios.json")
            for u in usuarios:
                if u.get("correo") == usuario.get("correo"):
                    u['contrasena'] = nueva_contrasena
                    break
            guardar_datos_en_json(usuarios, "usuarios.json")
            # Redirigir a la página de éxito
            return redirect(url_for('restablecimiento_exitoso'))
        return render_template('nueva_contrasenia.html', token=token)
    else:
        # Informar al usuario que el token es inválido o ha expirado
        return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
