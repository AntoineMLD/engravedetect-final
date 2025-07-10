import smtplib
from email.mime.text import MIMEText
from ..config import settings

def send_confirmation_email(email: str, token: str) -> None:
    """
    Envoie un email de confirmation avec un lien contenant le token JWT.

    Args:
        email (str): Adresse email du destinataire
        token (str): Token JWT de confirmation
    """
    confirmation_link = f"https://engravedetect.fr/confirm?token={token}"

    body = f"""Bonjour,

Merci pour votre inscription sur EngraveDetect.

Veuillez confirmer votre adresse en cliquant sur ce lien :
{confirmation_link}

Si vous n'avez pas demandé cette inscription, ignorez simplement ce message.

Cordialement,
L'équipe EngraveDetect"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Confirmez votre inscription sur EngraveDetect"
    msg["From"] = settings.SMTP_SENDER
    msg["To"] = email

    try:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_SENDER, [email], msg.as_string())
        print(f"[EMAIL ENVOYÉ] Confirmation envoyée à {email}")
    except Exception as e:
        print(f"[ERREUR EMAIL] Impossible d'envoyer l'email à {email}: {e}")
        raise
