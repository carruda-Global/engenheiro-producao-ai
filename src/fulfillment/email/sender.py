import os, smtplib, logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER", "")
        self.password = os.getenv("SMTP_PASS", "")
        self.from_email = os.getenv("FROM_EMAIL", "contato@global-engenharia.com")
        self.from_name = os.getenv("FROM_NAME", "AION 7.0")

    @property
    def is_configured(self) -> bool:
        return bool(self.user and self.password)

    def send(self, to: str, subject: str, html: str) -> dict:
        if not self.is_configured:
            logger.warning("SMTP nao configurado")
            return {"status": "skipped"}
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html", "utf-8"))
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            logger.info(f"Email enviado para {to}: {subject}")
            return {"status": "sent"}
        except Exception as e:
            logger.error(f"Falha ao enviar email: {e}")
            return {"status": "error", "error": str(e)}
