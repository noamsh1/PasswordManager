import random

MINIMUM_PASSWORD_LENGTH = 8    # Minimum length required for a password to be considered strong
MAXIMUM_PASSWORD_LENGTH = 64    # Maximum allowed password length
DEFAULT_LENGTH = 16    # Default generated password length
DEFAULT_SPECIAL = "-_!?@#$%^&*/|"    # Default set of allowed special characters
DEFAULT_SETTINGS = {"max_length" : DEFAULT_LENGTH,
                    "include" : {"Upper" : True, "Lower" : True, "Number" : True, "Special" : True},
                    "special_allowed" : DEFAULT_SPECIAL,
                    "start" : {"Upper" : True, "Lower" : True, "Number" : True, "Special" : True},
                    "special_allowed_start" : DEFAULT_SPECIAL}

UPPER_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWER_SET = "abcdefghijklmnopqrstuvwxyz"
NUM_SET = "0123456789"


class PasswordHandler:

    @staticmethod
    def generate_password(preferences):
        """Receives a preferences dict and generates a random password that satisfies the given rules.
        Ensures the first character matches the start rules and that at least one character from each
        included category is present."""
        length = preferences["max_length"]
        include_rules = preferences["include"]
        start_rules = preferences["start"]
        password = ""
        start_set = ""
        if start_rules["Upper"]:
            start_set += UPPER_SET
        if start_rules["Lower"]:
            start_set += LOWER_SET
        if start_rules["Number"]:
            start_set += NUM_SET
        if start_rules["Special"]:
            start_set += preferences["special_allowed_start"]
        password = random.choice(start_set)

        full_password_set = ""
        mandatory_chars = ""
        if include_rules["Upper"]:
            full_password_set += UPPER_SET
            mandatory_chars += random.choice(UPPER_SET)
        if include_rules["Lower"]:
            full_password_set += LOWER_SET
            mandatory_chars += random.choice(LOWER_SET)
        if include_rules["Number"]:
            full_password_set += NUM_SET
            mandatory_chars += random.choice(NUM_SET)
        if include_rules["Special"]:
            full_password_set += preferences["special_allowed"]
            mandatory_chars += random.choice(preferences["special_allowed"])

        remaining_password = list(mandatory_chars)
        
        for i in range(length - len(remaining_password) - 1):
            remaining_password.append(random.choice(full_password_set))
        random.shuffle(remaining_password)
        shuffled_password = "".join(remaining_password)
        password += shuffled_password
        return password
    

    @staticmethod
    def is_strong_password(password):
        """Receives a password and returns True if it meets the minimum strength requirements:
        at least 8 characters, with uppercase, lowercase, digit, and special character."""
        if len(password) >= MINIMUM_PASSWORD_LENGTH and any(char.islower() for char in password) and any(char.isupper() for char in password) and any(char.isdigit() for char in password) and any(not char.isalnum() for char in password):
            return True
        else:
            return False
    