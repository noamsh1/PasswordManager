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
        self._security_context = ssl.create_default_context()

    def send_gmail(self, recipient_gmail, msg):
        with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context = self._security_context) as server:
            server.login(SENDER_GMAIL, SENDER_GMAIL_PASSWORD)
            server.sendmail(SENDER_GMAIL, recipient_gmail, msg)
    
    def send_login_code_gmail(self, recipient_gmail):
        login_code = self._generate_login_code()
        login_msg_with_code = LOGIN_CODE_MSG.format(code = login_code)
        self.send_gmail(recipient_gmail, login_msg_with_code)
        code_creation_time = datetime.datetime.now()
        return (login_code, code_creation_time)

    def _generate_login_code(self):
        login_code = "".join(secrets.choice(string.digits) for _ in range(8))
        return login_code