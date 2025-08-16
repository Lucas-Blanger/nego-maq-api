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


@auth_routes.route('/editar', methods=['PUT'])
def editar_perfil():
    data = request.get_json()
    email_atual = data.get('email_atual') # Email atual do usuário para identificação

    if not email_atual:
        return jsonify({'erro': 'Email atual é obrigatório'}), 400
    
    usuario = Usuario.query.filter_by(email=email_atual).first()

    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    # Atualizando campos se fornecidos
    novo_nome = data.get('nome')
    novo_email = data.get('novo_email')
    novo_telefone = data.get('novo_telefone')
    nova_senha = data.get('nova_senha')

    if novo_nome:
        usuario.nome = novo_nome

    if novo_email:
        # Verifica se o novo email já está em uso
        if Usuario.query.filter_by(email=novo_email).first():
            return jsonify({'erro': 'Novo email já está em uso'}), 400
        usuario.email = novo_email

    if nova_senha:
        usuario.set_senha(nova_senha)

    db.session.commit()
    return jsonify({'mensagem': 'Perfil atualizado com sucesso'})