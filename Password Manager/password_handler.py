import random

MINIMUM_PASSWORD_LENGTH = 10
CHARACTER_SET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_!@#$%^&*/|"

class PasswordHandler:

    @staticmethod
    def generate_password(length):
        password = ""
        for i in range(length):
            password += random.choice(CHARACTER_SET)
        return password
    

    @staticmethod
    def is_strong_password(password):
        if len(password) >= MINIMUM_PASSWORD_LENGTH and any(char.islower() for char in password) and any(char.isupper() for char in password) and any(char.isdigit() for char in password) and any(not char.isalnum() for char in password):
            return True
        else:
            return False
    