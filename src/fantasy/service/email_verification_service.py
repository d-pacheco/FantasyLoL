import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.common.schemas.verification_email_config import VerificationConfig


class EmailVerificationService:
    def __init__(self, verification_config: VerificationConfig = VerificationConfig()):
        self.verification_config = verification_config

    def send_verification_email(self, user_email: str, token: str) -> bool:
        verification_link = f"{self.verification_config.domain_url}" \
                            f"/fantasy/v1/user/verify-email/{token}"
        subject = "Verify your email address"
        body = f"Click the link to verify your email: {verification_link}"

        sender_email = self.verification_config.sender_email
        password = self.verification_config.sender_password

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = user_email
            text_part = MIMEText(body, "plain")
            message.attach(text_part)

            with smtplib.SMTP_SSL(
                    self.verification_config.smtp_host,
                    self.verification_config.smtp_port) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, user_email, message.as_string())
        except Exception as e:
            print(f"Failed to send verification email: {e}")
            return False
        return True
