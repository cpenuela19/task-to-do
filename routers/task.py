from flask import Blueprint, request, flash, redirect, url_for
from extensions import db
from models import Task, CategoriaEnum, EstadoEnum, Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date

task_bp = Blueprint('task', __name__)

@task_bp.route('/usuarios/<int:id_usuario>/tareas', methods=['GET'])
@jwt_required()
def obtener_tareas(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    tareas = Task.query.filter_by(ID_Usuario=id_usuario).all()
    flash(f"Mostrando tareas para el usuario {usuario.nombre_usuario}.", "info")
    return redirect(url_for('vista_tareas'))

@task_bp.route('/tareas', methods=['POST'])
@jwt_required()
def crear_tarea():
    data = request.form  
    user_id = get_jwt_identity()

    texto_tarea = data.get("texto_tarea")
    fecha_tentativa_finalizacion = data.get("fecha_tentativa_finalizacion")
    categoria = data.get("categoria", CategoriaEnum.SIN_CATEGORIA.value)
    estado = data.get("estado", EstadoEnum.PENDIENTE.value)

    if not texto_tarea:
        flash("El texto de la tarea es obligatorio.", "error")
        return redirect(url_for('vista_tareas'))

    if categoria not in [cat.value for cat in CategoriaEnum]:
        flash("Categoría inválida.", "error")
        return redirect(url_for('vista_tareas'))

    if estado not in [est.value for est in EstadoEnum]:
        flash("Estado inválido.", "error")
        return redirect(url_for('vista_tareas'))

    if fecha_tentativa_finalizacion:
        try:
            fecha_tentativa = date.fromisoformat(fecha_tentativa_finalizacion)
            if fecha_tentativa < date.today():
                flash("La fecha tentativa no puede ser anterior a hoy.", "error")
                return redirect(url_for('vista_tareas'))
        except ValueError:
            flash("Fecha tentativa inválida.", "error")
            return redirect(url_for('vista_tareas'))
    else:
        fecha_tentativa = None

    nueva_tarea = Task(
        texto_tarea=texto_tarea,
        fecha_tentativa_finalizacion=fecha_tentativa,
        estado=EstadoEnum(estado),
        categoria=CategoriaEnum(categoria),
        ID_Usuario=user_id
    )
    db.session.add(nueva_tarea)
    db.session.commit()

    flash("Tarea creada exitosamente.", "success")
    return redirect(url_for('vista_tareas'))

@task_bp.route('/tareas/<int:id>', methods=['POST'])
@jwt_required()
def actualizar_tarea(id):
    data = request.form  
    tarea = Task.query.get_or_404(id)

    texto_tarea = data.get("texto_tarea")
    if texto_tarea:
        tarea.texto_tarea = texto_tarea

    estado = data.get("estado")
    if estado:
        if estado not in [est.value for est in EstadoEnum]:
            flash("Estado inválido.", "error")
            return redirect(url_for('vista_tareas'))
        tarea.estado = EstadoEnum(estado)

    db.session.commit()
    flash("Tarea actualizada exitosamente.", "success")
    return redirect(url_for('vista_tareas'))

@task_bp.route('/tareas/<int:id>', methods=['POST'])
@jwt_required()
def eliminar_tarea(id):
    tarea = Task.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    flash("Tarea eliminada exitosamente.", "success")
    return redirect(url_for('vista_tareas'))

@task_bp.route('/tareas/<int:id>', methods=['GET'])
@jwt_required()
def obtener_tarea_por_id(id):
    tarea = Task.query.get_or_404(id)
    flash(f"Tarea '{tarea.texto_tarea}' obtenida con éxito.", "info")
    return redirect(url_for('vista_tareas'))
