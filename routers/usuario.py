from flask import Blueprint, request, jsonify, redirect, url_for, flash, session
from extensions import db
from models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/', methods=['POST'])
def crear_usuario():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    nombre_usuario = data.get('nombre_usuario', "").strip()
    contrasena = data.get('contrasena')
    imagen_perfil = data.get('imagen_perfil')

    if not nombre_usuario:
        flash("El nombre de usuario es obligatorio", "error")
        return redirect(url_for('registro'))
    
    if not contrasena:
        flash("La contraseña es obligatoria", "error")
        return redirect(url_for('registro'))
    
    if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
        flash("El nombre de usuario ya existe", "error")
        return redirect(url_for('registro'))
    
    if not imagen_perfil:
        imagen_perfil = 'default-picture.jpg'

    # Hashear la contraseña y crear el usuario
    hashed_password = generate_password_hash(contrasena)
    nuevo_usuario = Usuario(
        nombre_usuario=nombre_usuario,
        contrasena=hashed_password,
        imagen_perfil=imagen_perfil
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    access_token = create_access_token(identity=str(nuevo_usuario.id))

    session['access_token'] = access_token

    flash("Usuario registrado exitosamente. Bienvenido a tu lista de tareas.", "success")
    return redirect(url_for('task.vista_tareas'))


# Login
@usuario_bp.route('/iniciar-sesion', methods=['POST'])
def iniciar_sesion():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    nombre_usuario = data.get('nombre_usuario')
    contrasena = data.get('contrasena')

    if not nombre_usuario or not contrasena:
        flash("Nombre de usuario o contraseña son obligatorios", "error")
        return redirect(url_for('index'))

    usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
    if not usuario or not check_password_hash(usuario.contrasena, contrasena):
        flash("Usuario o contraseña incorrectos", "error")
        return redirect(url_for('index'))

    access_token = create_access_token(identity=str(usuario.id))


    session['access_token'] = access_token
    flash("Inicio de sesión exitoso", "success")
    
    return redirect(url_for('task.vista_tareas'))
