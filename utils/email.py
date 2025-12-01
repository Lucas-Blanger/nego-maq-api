import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def enviar_email(destinatario, assunto, corpo):

    thread = threading.Thread(
        target=_enviar_email_thread, args=(destinatario, assunto, corpo)
    )
    thread.daemon = True
    thread.start()
    return True


def _enviar_email_thread(destinatario, assunto, corpo):
    """
    Função interna que realmente envias o email
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        print("AVISO: Credenciais SMTP não configuradas")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "html"))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"Email enviado com sucesso para {destinatario}")
        return True

    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False
