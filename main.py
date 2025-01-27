from flask import Flask, flash, jsonify, redirect, render_template, session, url_for
import os
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import CategoriaEnum, Task
from routers.usuario import usuario_bp
from routers.task import task_bp
from extensions import db, jwt
import secrets

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'a3f5b8c3d4e2f1a9b1c6d9e8f7a5c3e4d2f1b9a8e7c6f5a4b3d2e1f0a8c7b6'  
app.secret_key = secrets.token_hex(32)

db.init_app(app)
jwt.init_app(app)


app.register_blueprint(usuario_bp, url_prefix='/usuarios')  
app.register_blueprint(task_bp, url_prefix='/tareas')  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/usuarios/registro', methods=['GET'])
def registro():
    return render_template('registro.html')

@app.route('/tareas', methods=['GET'])
def vista_tareas():
    # Verificar si el token está en la sesión
    access_token = session.get('access_token')
    if not access_token:
        flash("Debes iniciar sesión para acceder a tus tareas.", "error")
        return redirect(url_for('index'))

    # Decodificar el token JWT
    from flask_jwt_extended import decode_token
    try:
        user_id = decode_token(access_token)["sub"]  # El ID del usuario (cadena)
        print(f"ID del usuario autenticado: {user_id}")
    except Exception as e:
        flash("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.", "error")
        print(f"Error al decodificar el token: {e}")
        return redirect(url_for('index'))

    # Obtener las tareas del usuario autenticado
    tareas = Task.query.filter_by(ID_Usuario=int(user_id)).all()
    categorias = [cat.value for cat in CategoriaEnum]
    return render_template('tareas.html', tareas=tareas, categorias=categorias)



if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Database created successfully')
    app.run(debug=True)


