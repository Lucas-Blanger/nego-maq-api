import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def enviar_email(destinatario, assunto, corpo):
    # Envia email usando SMTP
    try:
        remetente = os.getenv("EMAIL_REMETENTE")
        senha = os.getenv("EMAIL_SENHA")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        mensagem = MIMEMultipart()
        mensagem["From"] = remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto

        mensagem.attach(MIMEText(corpo, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(mensagem)

        return True
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False
