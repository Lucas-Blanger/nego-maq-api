from flask import Blueprint, request, jsonify
from database.models import Usuario
from database import db

auth_routes = Blueprint('auth', __name__, url_prefix='/auth')

@auth_routes.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400
    usuario = Usuario(
        nome=data['nome'],
        email=data['email'],
        is_admin=data.get('is_admin', False)
    )
    usuario.set_senha(data['senha'])
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado com sucesso'})

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = Usuario.query.filter_by(email=data['email']).first()
    if usuario and usuario.checar_senha(data['senha']):
        return jsonify({'mensagem': 'Login realizado com sucesso', 'is_admin': usuario.is_admin})
    return jsonify({'erro': 'Credenciais inválidas'}), 401


@auth_routes.route('/recuperar', methods=['POST'])
def recuperar_senha():
    data = request.get_json()
    email = data.get('email')
    nova_senha = data.get('nova_senha')
    if not email or not nova_senha:
        return jsonify({'erro': 'Email e nova senha são obrigatórios'}), 400
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    usuario.set_senha(nova_senha)
    db.session.commit()

    return jsonify({'mensagem': 'Senha atualizada com sucesso'})