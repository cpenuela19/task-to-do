from flask import Flask, render_template
import os
from routers.usuario import usuario_bp
from routers.task import task_bp
from extensions import db, jwt

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'a3f5b8c3d4e2f1a9b1c6d9e8f7a5c3e4d2f1b9a8e7c6f5a4b3d2e1f0a8c7b6'  

db.init_app(app)
jwt.init_app(app)


app.register_blueprint(usuario_bp, url_prefix='/usuarios')  
app.register_blueprint(task_bp, url_prefix='/tareas')  

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Database created successfully')

        # #tester1
        # usuario = Usuario(nombre_usuario="prueba122", contrasena="12345")
        # db.session.add(usuario)
        # db.session.commit()

        # tarea = Task(
        #     texto_tarea="Esta es una tarea de prueba",
        #     ID_Usuario=usuario.id,
        #     categoria=CategoriaEnum.TRABAJO,
        #     estado=EstadoEnum.EN_PROGRESO,
        #     fecha_tentativa_finalizacion=date(2025, 1, 31)
        # )
        # db.session.add(tarea)
        # db.session.commit()

        # usuarios = Usuario.query.all()
        # tareas = Task.query.all()
        # print("Usuarios:", [u.nombre_usuario for u in usuarios])
        # print("Tareas:", [t.texto_tarea for t in tareas])

    app.run(debug=True)


