from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from enum import Enum
from datetime import date

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Enumeracion de categorias
class CategoriaEnum(Enum):
    HOGAR = 'Hogar'
    TRABAJO = 'Trabajo'
    UNIVERSIDAD = 'Universidad'
    URGENTE = 'Urgente'
    OTROS = 'Otros'
    SIN_CATEGORIA = 'Sin categoria'

#Enumeracion de estados
class EstadoEnum(Enum):
    PENDIENTE = 'Pendiente'
    EN_PROGRESO = 'En progreso'
    FINALIZADO = 'Finalizado'

#Modelo usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), nullable=False, unique=True)
    contrasena = db.Column(db.String(50), nullable=False)
    imagen_perfil = db.Column(db.String(100), nullable=True, default='default-picture.jpg')

    tasks = db.relationship('Task', back_populates='usuario', cascade='delete-orphan')


#Modelo task

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    texto_tarea = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.Date, nullable=False, default=date.today)
    fecha_tentativa_finalizacion = db.Column(db.Date, nullable=True)
    estado = db.Column(db.Enum(EstadoEnum), nullable=False, default=EstadoEnum.PENDIENTE)
    categoria = db.Column(db.Enum(CategoriaEnum), nullable=False, default=CategoriaEnum.SIN_CATEGORIA)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='tasks')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Database created?')
    app.run(debug=True)

