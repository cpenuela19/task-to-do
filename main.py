from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
import os
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import CategoriaEnum, Task
from routers.usuario import usuario_bp
from routers.task import task_bp
from extensions import db, jwt
import secrets
from datetime import datetime

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

@app.template_filter('date')
def format_date(value, format='%Y-%m-%d'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/usuarios/registro', methods=['GET'])
def registro():
    return render_template('registro.html')


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Database created successfully')
    app.run(host="0.0.0.0", port=5000, debug=True)



