from flask import Blueprint, request, jsonify
from extensions import db
from models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

usuario_bp = Blueprint('usuario', __name__)

#Crear un usuario
@usuario_bp.route('/', methods = ['POST'])
def crear_usuario():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    nombre_usuario = data.get('nombre_usuario', "").strip()
    contrasena = data.get('contrasena')
    imagen_perfil = data.get('imagen_perfil')

    if not nombre_usuario:
        return jsonify({'message': 'El nombre de usuario es obligatorio'}), 400
    
    if not contrasena:
        return jsonify({'message': 'La contraseña es obligatoria'}), 400
    
    if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
        return jsonify({'message': 'El nombre de usuario ya existe'}), 400
    
    if not imagen_perfil:
        imagen_perfil = 'default-picture.jpg'

    hashed_password = generate_password_hash(contrasena)
    nuevo_usuario = Usuario(
        nombre_usuario=nombre_usuario,
        contrasena=hashed_password,
        imagen_perfil=imagen_perfil
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "message": "Usuario creado exitosamente",
        "id": nuevo_usuario.id,
        "nombre_usuario": nuevo_usuario.nombre_usuario,
        "imagen_perfil": nuevo_usuario.imagen_perfil
    }), 201

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
        return jsonify({"message": "Nombre de usuario o contraseña son obligatorios"}), 400

    usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
    if not usuario or not check_password_hash(usuario.contrasena, contrasena):
        return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

    access_token = create_access_token(identity={"id": usuario.id, "nombre_usuario": usuario.nombre_usuario})
    return jsonify({"access_token": access_token}), 200

