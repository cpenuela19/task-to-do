from flask import Blueprint, request, jsonify
from main import db, Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

usuario_bp = Blueprint('usuario', __name__)

#Crear un usuario
@usuario_bp.route('/', methods = ['POST'])
def crear_usuario():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    contrasena = data.get('contrasena')
    imagen_perfil = data.get('imagen_perfil')

    


