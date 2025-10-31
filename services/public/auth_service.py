from datetime import datetime, timedelta
import random
import string
from database import db
from database.models import Usuario
from utils.jwt_utils import gerar_token
from utils.crypto_utils import criptografar_cpf, descriptografar_cpf
from utils.email import enviar_email


# Registra um novo usuário
def registrar(nome, sobrenome, email, telefone, cpf, senha, is_admin=False):
    """Registra um novo usuário"""
    if Usuario.query.filter_by(email=email).first():
        raise ValueError("Email já cadastrado")

    cpf_limpo = None
    if cpf:
        cpf_limpo = cpf.replace(".", "").replace("-", "").strip()
        if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
            raise ValueError("CPF inválido")

        usuarios_com_cpf = Usuario.query.filter(Usuario.cpf.isnot(None)).all()
        for u in usuarios_com_cpf:
            if descriptografar_cpf(u.cpf) == cpf_limpo:
                raise ValueError("CPF já cadastrado")

    usuario = Usuario(
        nome=nome,
        sobrenome=sobrenome,
        email=email,
        telefone=telefone,
        cpf=criptografar_cpf(cpf_limpo),
        is_admin=is_admin,
    )
    usuario.set_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    token = gerar_token(usuario)
    return usuario, token


# Faz login do usuário
def login(email, senha):
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and usuario.checar_senha(senha):
        token = gerar_token(usuario)
        return usuario, token
    raise ValueError("Credenciais inválidas")


# Edita o perfil do usuário
def editar_perfil(
    email_atual,
    novo_nome=None,
    novo_sobrenome=None,
    novo_email=None,
    novo_telefone=None,
    novo_cpf=None,
    nova_senha=None,
):
    """Atualiza dados do usuário"""
    usuario = Usuario.query.filter_by(email=email_atual).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")

    if novo_nome:
        usuario.nome = novo_nome

    if novo_sobrenome:
        usuario.sobrenome = novo_sobrenome

    if novo_email:
        if Usuario.query.filter_by(email=novo_email).first():
            raise ValueError("Novo email já está em uso")
        usuario.email = novo_email

    if novo_telefone:
        usuario.telefone = novo_telefone

    if novo_cpf:
        cpf_limpo = novo_cpf.replace(".", "").replace("-", "").strip()
        if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
            raise ValueError("CPF inválido")

        usuarios_com_cpf = Usuario.query.filter(
            Usuario.cpf.isnot(None), Usuario.id != usuario.id
        ).all()
        for u in usuarios_com_cpf:
            if descriptografar_cpf(u.cpf) == cpf_limpo:
                raise ValueError("CPF já cadastrado")

        usuario.cpf = criptografar_cpf(cpf_limpo)

    if nova_senha:
        usuario.set_senha(nova_senha)

    db.session.commit()
    return usuario


def gerar_codigo_recuperacao():
    # Gera um código de 6 dígitos
    return "".join(random.choices(string.digits, k=6))


def solicitar_recuperacao_senha(email):
    # Envia código de recuperação para o email do usuário
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")

    # Gera código e define expiração (15 minutos)
    codigo = gerar_codigo_recuperacao()
    expiracao = datetime.utcnow() + timedelta(minutes=15)

    usuario.codigo_recuperacao = codigo
    usuario.codigo_expiracao = expiracao
    db.session.commit()

    assunto = "Código de Recuperação - NegoMaq Couros & Facas"
    corpo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        
                        <tr>
                            <td style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 40px 30px; text-align: center;">
                                <img src="https://res.cloudinary.com/dq4catqou/image/upload/v1761932437/p2jof6awhzpzjiddfk7d.png" alt="Logo NegoMaq" width="120" style="margin-bottom: 15px; border-radius: 8px;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;">
                                    COUROS<span style="color: #ff3333;">NEGO</span>MAQ
                                 </h1>
                                <p style="color: #cccccc; margin: 10px 0 0 0; font-size: 14px; letter-spacing: 1px;">
                                    COUROS & FACAS ARTESANAIS
                                </p>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">
                                    Recuperação de Senha
                                </h2>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Olá <strong style="color: #333333;">{usuario.nome}</strong>,
                                </p>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Recebemos uma solicitação para redefinir a senha da sua conta. 
                                    Use o código de verificação abaixo para continuar:
                                </p>
                                
                                <!-- Box do Código -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                    <tr>
                                        <td style="background: linear-gradient(135deg, #ff3333 0%, #cc0000 100%); border-radius: 8px; padding: 30px; text-align: center;">
                                            <p style="color: #ffffff; font-size: 14px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 2px;">
                                                Seu Código de Verificação
                                            </p>
                                            <h1 style="color: #ffffff; margin: 0; font-size: 48px; font-weight: bold; letter-spacing: 12px; font-family: 'Courier New', monospace;">{codigo}</h1>
                                        </td>
                                    </tr>
                                </table>
                                
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fff8e1; border-left: 4px solid #ffc107; border-radius: 4px; padding: 15px; margin: 20px 0;">
                                    <tr>
                                        <td>
                                            <p style="color: #856404; font-size: 14px; margin: 0; line-height: 1.6;">
                                                <strong>Este código expira em 15 minutos.</strong><br>
                                                Por segurança, não compartilhe este código com ninguém.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #666666; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                                    Se você não solicitou esta recuperação de senha, por favor ignore este email. 
                                    Sua conta permanecerá segura.
                                </p>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="background-color: #1a1a1a; padding: 30px; text-align: center; border-top: 3px solid #ff3333;">
                                <p style="color: #cccccc; font-size: 14px; margin: 0 0 10px 0;">
                                    <strong style="color: #ffffff;">NegoMaq Couros & Facas</strong>
                                </p>
                                <p style="color: #999999; font-size: 12px; margin: 0 0 15px 0; line-height: 1.5;">
                                    Fabricante de Artefatos em Couros 100% Legítimo<br>
                                    Especialista em Avental Churrasqueiro
                                </p>
                                <p style="color: #666666; font-size: 11px; margin: 0;">
                                    © 2025 NegoMaq. Todos os direitos reservados.
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    if not enviar_email(usuario.email, assunto, corpo):
        raise ValueError("Erro ao enviar email. Tente novamente.")

    return usuario


def verificar_codigo_e_redefinir_senha(email, codigo, nova_senha):
    # Verifica o código e redefine a senha
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        raise ValueError("Usuário não encontrado")

    if not usuario.codigo_recuperacao:
        raise ValueError("Nenhum código de recuperação foi solicitado")

    if usuario.codigo_expiracao < datetime.utcnow():
        # Limpa o código expirado
        usuario.codigo_recuperacao = None
        usuario.codigo_expiracao = None
        db.session.commit()
        raise ValueError("Código expirado. Solicite um novo código")

    if usuario.codigo_recuperacao != codigo:
        raise ValueError("Código inválido")

    # Atualiza a senha e limpa o código
    usuario.set_senha(nova_senha)
    usuario.codigo_recuperacao = None
    usuario.codigo_expiracao = None
    db.session.commit()

    return usuario
