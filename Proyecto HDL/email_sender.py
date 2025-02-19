import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import re
import logging
import os

class EmailSender:
    """Clase para manejar el envío de emails"""
    
    def __init__(self, smtp_server: str, port: int, email: str, password: str):
        self.smtp_server = smtp_server
        self.port = port
        self.email = email
        self.password = password
        self._validate_credentials()

    def _validate_credentials(self) -> None:
        """Valida las credenciales de email"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Email inválido")
        if len(self.password) < 8:
            raise ValueError("Contraseña demasiado corta")

    def send_email(self, to: str, subject: str, body: str, file_path: str, is_html=False) -> None:
        """Envía un email con adjunto"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))
            
            
            self._attach_file(msg, file_path)
            
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logging.info(f"Email enviado a {to}")
        except Exception as e:
            logging.error(f"Error enviando email: {str(e)}")
            raise

    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Adjunta un archivo al mensaje"""
        filename = os.path.basename(file_path)
        file_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        main_type, sub_type = file_type.split('/', 1)
        
        with open(file_path, "rb") as f:
            part = MIMEBase(main_type, sub_type)
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)