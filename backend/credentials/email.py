import os # Add os module for environment variable access
import smtplib # Add smtplib for sending emails
from email.mime.text import MIMEText # Add MIMEText for creating email content
from email.mime.multipart import MIMEMultipart # Add MIMEMultipart for creating multipart email
from email.mime.image import MIMEImage # Add MIMEImage for adding images to email
import sqlite3 # Add sqlite3 for database operations

dbconn = sqlite3.connect('/app/data/database.db', check_same_thread=False)

def send_invitation_email(token: str):

    # Get invitation info from the database
    invitation = dbconn.execute(
        "SELECT email, language, expires_at FROM invitations WHERE code = ?",
        (token,)
    ).fetchone()

    if not invitation:
        raise ValueError("Invalid invitation token")
    
    email, language, expires_at = invitation

    # Get email server settings from environment variables
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))  # Default to 587 if not set
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_username or not smtp_password:
        raise ValueError("CREDENTIALS_NOT_CONFIGURED")
    
    # Translations
    translations = {
        "en": {
            "subject": "Your Taxtor Invitation",
            "title": "You have been invited to join Taxtor!",
            "message": "You have received an invitation to create a Taxtor account.",
            "token_label": "Your invitation code is:",
            "continue": "To continue, go to the Taxtor registration page and enter the invitation code.",
            "expire": "This invitation will expire on {expires_at}.",
            "thanks": "Thank you for using Taxtor!"
        },
        "es": {
            "subject": "Tu invitación a Taxtor",
            "title": "¡Has sido invitado a unirte a Taxtor!",
            "message": "Has recibido una invitación para crear una cuenta de Taxtor.",
            "token_label": "Tu código de invitación es:",
            "continue": "Para continuar, ve a la página de registro de Taxtor e ingresa el código de invitación.",
            "expire": "Esta invitación expirará el {expires_at}.",
            "thanks": "¡Gracias por usar Taxtor!"
        },
        "fr": {
            "subject": "Votre invitation à Taxtor",
            "title": "Vous avez été invité à rejoindre Taxtor !",
            "message": "Vous avez reçu une invitation pour créer un compte Taxtor.",
            "token_label": "Votre code d'invitation est :",
            "continue": "Pour continuer, rendez-vous sur la page d'inscription de Taxtor et entrez le code d'invitation.",
            "expire": "Cette invitation expirera le {expires_at}.",
            "thanks": "Merci d'utiliser Taxtor !"
        }
    }

    translation = translations.get(language, translations["en"])

    # Create the email content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="{language}">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
     <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            font-family: Arial, Helvetica, sans-serif;
        }}

        .container {{
            max-width: 600px;
            margin: 40px auto;
            padding: 40px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            color: #222222;
            margin-bottom: 20px;
        }}

        p {{
            color: #555555;
            font-size: 16px;
            line-height: 1.6;
        }}

        .token_label {{
            margin-top: 30px;
            margin-bottom: 8px;
            font-size: 14px;
            font-weight: bold;
            color: #333333;
        }}

        .token_box {{
            padding: 18px;
            background-color: #f1f1f1;
            border: 2px solid #222222;
            border-radius: 8px;
            text-align: center;
            font-family: monospace;
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 1px;
            word-break: break-all;
        }}

        .expiration {{
            margin-top: 25px;
            font-size: 13px;
            color: #888888;
        }}
    </style>
    </head>

    <body>
        <div class="container">

            <img src="cid:logo" alt="Taxtor Logo" style="width: 150px; height: auto; margin-bottom: 20px;">
            <h1>{translation['title']}</h1>
            <p>{translation['message']}</p>
            <p class="token_label">{translation['token_label']}</p>
            <div class="token_box">{token}</div>
            <p>{translation['continue']}</p>
            <p class="expiration">{translation['expire'].format(expires_at=expires_at)}</p>
            <p class="thanks">{translation['thanks']}</p>
        </div>
    </body>
    </html>
    """

    # Create the email message
    msg = MIMEMultipart("alternative")
    
    msg["From"] = smtp_username
    msg["To"] = email
    msg["Subject"] = translation["subject"]

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with open("/app/credentials/assets/logo.png", "rb") as f:
        logo = MIMEImage(f.read())

    logo.add_header("Content-ID", "<logo>")

    logo.add_header("Content-Disposition", "inline", filename="logo.png")

    msg.attach(logo)

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, email, msg.as_string())