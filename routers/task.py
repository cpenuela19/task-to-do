from flask import Blueprint, request, jsonify
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
    return jsonify([
        {
            "id": tarea.id,
            "texto_tarea": tarea.texto_tarea,
            "fecha_creacion": tarea.fecha_creacion,
            "fecha_tentativa_finalizacion": tarea.fecha_tentativa_finalizacion,
            "estado": tarea.estado.value,
            "categoria": tarea.categoria.value
        }
        for tarea in tareas
    ]), 200

@task_bp.route('/tareas', methods=['POST'])
@jwt_required()
def crear_tarea():
    data = request.get_json()
    user_id = get_jwt_identity()["id"]

    texto_tarea = data.get("texto_tarea")
    fecha_tentativa_finalizacion = data.get("fecha_tentativa_finalizacion")
    categoria = data.get("categoria", CategoriaEnum.SIN_CATEGORIA.value)
    estado = data.get("estado", EstadoEnum.PENDIENTE.value)

    if not texto_tarea:
        return jsonify({"message": "El texto de la tarea es obligatorio"}), 400

    if categoria not in [cat.value for cat in CategoriaEnum]:
        return jsonify({"message": "Categoría inválida"}), 400

    if estado not in [est.value for est in EstadoEnum]:
        return jsonify({"message": "Estado inválido"}), 400

    if fecha_tentativa_finalizacion:
        try:
            fecha_tentativa = date.fromisoformat(fecha_tentativa_finalizacion)
            if fecha_tentativa < date.today():
                return jsonify({"message": "La fecha tentativa no puede ser anterior de hoy"}), 400
        except ValueError:
            return jsonify({"message": "Fecha tentativa inválida"}), 400
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

    return jsonify({"message": "Tarea creada exitosamente"}), 201

@task_bp.route('/tareas/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_tarea(id):
    data = request.get_json()
    tarea = Task.query.get_or_404(id)

    texto_tarea = data.get("texto_tarea")
    if texto_tarea:
        tarea.texto_tarea = texto_tarea

    estado = data.get("estado")
    if estado:
        if estado not in [est.value for est in EstadoEnum]:
            return jsonify({"message": "Estado inválido"}), 400
        tarea.estado = EstadoEnum(estado)

    db.session.commit()
    return jsonify({"message": "Tarea actualizada exitosamente"}), 200

@task_bp.route('/tareas/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_tarea(id):
    tarea = Task.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    return jsonify({"message": "Tarea eliminada exitosamente"}), 200

@task_bp.route('/tareas/<int:id>', methods=['GET'])
@jwt_required()
def obtener_tarea_por_id(id):
    tarea = Task.query.get_or_404(id)
    return jsonify({
        "id": tarea.id,
        "texto_tarea": tarea.texto_tarea,
        "fecha_creacion": tarea.fecha_creacion.strftime('%Y-%m-%d'),
        "fecha_tentativa_finalizacion": tarea.fecha_tentativa_finalizacion.strftime('%Y-%m-%d') if tarea.fecha_tentativa_finalizacion else None,
        "estado": tarea.estado.value,
        "categoria": tarea.categoria.value
    }), 200