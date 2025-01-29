from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from extensions import db
from models import Task, CategoriaEnum, EstadoEnum, Usuario
from flask_jwt_extended import decode_token, jwt_required, get_jwt_identity
from datetime import date

task_bp = Blueprint('task', __name__)

@task_bp.route('/', methods=['GET'])
def vista_tareas():
    access_token = session.get('access_token')
    if not access_token:
        flash("Debes iniciar sesión para acceder a tus tareas.", "error")
        return redirect(url_for('index'))

    from flask_jwt_extended import decode_token
    try:
        user_id = decode_token(access_token)["sub"]  
        print(f"ID del usuario autenticado: {user_id}")
    except Exception as e:
        flash("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.", "error")
        print(f"Error al decodificar el token: {e}")
        return redirect(url_for('index'))

    tareas = Task.query.filter_by(ID_Usuario=int(user_id)).all()
    categorias = [cat.value for cat in CategoriaEnum]
    return render_template('tareas.html', tareas=tareas, categorias=categorias)


@task_bp.route('/usuarios/<int:id_usuario>/tareas', methods=['GET'])
@jwt_required()
def obtener_tareas(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    tareas = Task.query.filter_by(ID_Usuario=id_usuario).all()
    flash(f"Mostrando tareas para el usuario {usuario.nombre_usuario}.", "info")
    return redirect(url_for('task.vista_tareas'))


@task_bp.route('/crear-tarea', methods=['POST'])
def crear_tarea():
    # Obtener el token de la sesión
    access_token = session.get('access_token')
    if not access_token:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for('index'))

    # Decodificar el token para obtener el ID del usuario
    from flask_jwt_extended import decode_token
    try:
        user_id = decode_token(access_token)["sub"]
    except Exception as e:
        flash("El token es inválido o ha expirado. Por favor, inicia sesión nuevamente.", "error")
        print(f"Error al decodificar el token: {e}")
        return redirect(url_for('index'))

    # Obtener los datos del formulario
    data = request.form
    texto_tarea = data.get("texto_tarea")
    fecha_tentativa_finalizacion = data.get("fecha_tentativa_finalizacion")
    categoria = data.get("categoria", CategoriaEnum.SIN_CATEGORIA.value)
    estado = data.get("estado", EstadoEnum.PENDIENTE.value)

    # Validaciones
    if not texto_tarea:
        flash("El texto de la tarea es obligatorio.", "error")
        return redirect(url_for('task.vista_tareas'))

    if categoria not in [cat.value for cat in CategoriaEnum]:
        flash("Categoría inválida.", "error")
        return redirect(url_for('task.vista_tareas'))

    if estado not in [est.value for est in EstadoEnum]:
        flash("Estado inválido.", "error")
        return redirect(url_for('task.vista_tareas'))

    if fecha_tentativa_finalizacion:
        try:
            fecha_tentativa = date.fromisoformat(fecha_tentativa_finalizacion)
            if fecha_tentativa < date.today():
                flash("La fecha tentativa no puede ser anterior a hoy.", "error")
                return redirect(url_for('task.vista_tareas'))
        except ValueError:
            flash("Fecha tentativa inválida.", "error")
            return redirect(url_for('task.vista_tareas'))
    else:
        fecha_tentativa = None

    # Crear la nueva tarea
    nueva_tarea = Task(
        texto_tarea=texto_tarea,
        fecha_tentativa_finalizacion=fecha_tentativa,
        estado=EstadoEnum(estado),
        categoria=CategoriaEnum(categoria),
        ID_Usuario=int(user_id)
    )
    db.session.add(nueva_tarea)
    db.session.commit()

    flash("Tarea creada exitosamente.", "success")
    return redirect(url_for('task.vista_tareas'))

@task_bp.route('/tareas/<int:id>/actualizar', methods=['POST'])
def actualizar_tarea(id):
    access_token = session.get('access_token')
    if not access_token:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for('index'))

    try:
        user_id = decode_token(access_token)["sub"]
    except Exception as e:
        flash("El token es inválido o ha expirado. Por favor, inicia sesión nuevamente.", "error")
        return redirect(url_for('index'))

    tarea = Task.query.get_or_404(id)
    if tarea.ID_Usuario != int(user_id):
        flash("No tienes permiso para actualizar esta tarea.", "error")
        return redirect(url_for('task.vista_tareas'))

    data = request.form
    texto_tarea = data.get("texto_tarea")
    estado = data.get("estado")

    if texto_tarea:
        tarea.texto_tarea = texto_tarea
    if estado and estado in [est.value for est in EstadoEnum]:
        tarea.estado = EstadoEnum(estado)

    db.session.commit()
    flash("Tarea actualizada exitosamente.", "success")
    return redirect(url_for('task.vista_tareas'))

# Eliminar una tarea
@task_bp.route('/tareas/<int:id>/eliminar', methods=['POST'])
def eliminar_tarea(id):
    # Obtener el token de la sesión
    access_token = session.get('access_token')
    if not access_token:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for('index'))

    # Decodificar el token para verificar autenticación
    try:
        user_id = decode_token(access_token)["sub"]
    except Exception as e:
        flash("El token es inválido o ha expirado. Por favor, inicia sesión nuevamente.", "error")
        print(f"Error al decodificar el token: {e}")
        return redirect(url_for('index'))

    # Buscar la tarea
    tarea = Task.query.get_or_404(id)
    if tarea.ID_Usuario != int(user_id):
        flash("No tienes permiso para eliminar esta tarea.", "error")
        return redirect(url_for('task.vista_tareas'))

    # Eliminar la tarea
    db.session.delete(tarea)
    db.session.commit()
    flash("Tarea eliminada exitosamente.", "success")
    return redirect(url_for('task.vista_tareas'))

# Obtener una tarea por ID
@task_bp.route('/tareas/<int:id>', methods=['GET'])
def obtener_tarea_por_id(id):
    # Obtener el token de la sesión
    access_token = session.get('access_token')
    if not access_token:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for('index'))

    # Decodificar el token para verificar autenticación
    try:
        user_id = decode_token(access_token)["sub"]
    except Exception as e:
        flash("El token es inválido o ha expirado. Por favor, inicia sesión nuevamente.", "error")
        print(f"Error al decodificar el token: {e}")
        return redirect(url_for('index'))

    # Buscar la tarea
    tarea = Task.query.get_or_404(id)
    if tarea.ID_Usuario != int(user_id):
        flash("No tienes permiso para acceder a esta tarea.", "error")
        return redirect(url_for('task.vista_tareas'))

    flash(f"Tarea '{tarea.texto_tarea}' obtenida con éxito.", "info")
    return redirect(url_for('task.vista_tareas'))