import smtplib
import ssl
import secrets
import string
import datetime

PORT = 465
SMTP_SERVER = "smtp.gmail.com"
SENDER_GMAIL = "mypassmanager10@gmail.com"
SENDER_GMAIL_PASSWORD = "jhbjotmuqxailhkt"
EMAIL_CODE_EXPIRATION_TIME = 45
LOGIN_CODE_MSG = """\
Subject: Password Manager Test

Your login code is {code}."""

class EmailManager:
    def __init__(self):
        self._security_context = ssl.create_default_context()    # SSL security context for SMTP connection

    def send_gmail(self, recipient_gmail, msg):
        """Receives a recipient email address and a message, and sends the message via Gmail SMTP."""
        with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context = self._security_context) as server:
            server.login(SENDER_GMAIL, SENDER_GMAIL_PASSWORD)
            server.sendmail(SENDER_GMAIL, recipient_gmail, msg)
    
    def send_login_code_gmail(self, recipient_gmail):
        """Receives a recipient email address, generates a one-time login code, sends it via Gmail
        and returns the code along with the time it was created."""
        login_code = self._generate_login_code()
        login_msg_with_code = LOGIN_CODE_MSG.format(code = login_code)
        self.send_gmail(recipient_gmail, login_msg_with_code)
        code_creation_time = datetime.datetime.now()
        return (login_code, code_creation_time)

    def _generate_login_code(self):
        """Generates and returns a random 8-digit login code."""
        login_code = "".join(secrets.choice(string.digits) for _ in range(8))
        return login_code