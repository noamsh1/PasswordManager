import sqlite3
import os
import hashlib
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


load_dotenv()

DEFAULT_DB_PATH = r".\Database\PasswordManager.db"
#DB_PATH = r"C:\Users\noams\OneDrive\Databases\PasswordManager.db"
SECURITY_QUESTIONS_LIST = ["What is the name of your grandmother from your father's side?",
                           "What was the house number of the house you lived in as a child? (digits)",
                           "What was the make and model of the first-ever mobile phone you owned?",
                           "What was the name of the first school you ever attended?",
                           "In what city did you have your first-ever job?",
                           "What was the name of the band performing in the first concert you ever attended?",
                           "What was the make and model of your first car?",
                           "What is the name of your oldest cousin?",
                           "What was the name of the hospital where you were born?",
                           "What was the name of the first company you ever worked for?",
                          ]

class DataBase:

    def __init__(self):
        self.users_keys = {}    # dictionary matching user_id to their DK encryption key

        init_db = False
        db_path = os.getenv("DB_PATH", DEFAULT_DB_PATH)
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_path):
            if db_dir:
                os.makedirs(db_dir)
            init_db = True
        self.conn = sqlite3.connect(db_path)    # SQLite connection object
        self.cur = self.conn.cursor()    # SQLite cursor object
        
        if init_db:
            self.init_db()



    def init_db(self):
        """Creates all database tables (USERS, PASSWORD_PREFERENCES, USER_SITE, SECURITY_QUESTIONS) and populates the security questions."""

        # create USERS table
        self.cur.execute("""CREATE TABLE "USERS" (
                            user_id	INTEGER,
                            password TEXT NOT NULL,
                            username TEXT NOT NULL UNIQUE,
                            password_salt BLOB NOT NULL,
                            email BLOB NOT NULL,
                            phone_number BLOB NOT NULL,
                            user_dk BLOB NOT NULL UNIQUE,
                            key_salt BLOB NOT NULL,
                            voice_signature BLOB,
                            face_encoding BLOB,
                            question_id_1 INTEGER NOT NULL,
                            answer_1 BLOB NOT NULL,
                            question_id_2 INTEGER NOT NULL,
                            answer_2 BLOB NOT NULL,
                            question_id_3 INTEGER NOT NULL,
                            answer_3 BLOB NOT NULL,
                            answers_salt BLOB NOT NULL,
                            FOREIGN KEY("question_id_1") REFERENCES "SECURITY_QUESTIONS"("question_id"),
                            FOREIGN KEY("question_id_2") REFERENCES "SECURITY_QUESTIONS"("question_id"),
                            FOREIGN KEY("question_id_3") REFERENCES "SECURITY_QUESTIONS"("question_id"),
                            PRIMARY KEY("user_id" AUTOINCREMENT)
                        )""")
        
        # create PASSWORD_PREFERENCES table
        self.cur.execute("""CREATE TABLE "PASSWORD_PREFERENCES" (
                            "preferences_id"	INTEGER,
                            "max_length"	INTEGER DEFAULT 16,
                            "include_upper"	BOOLEAN DEFAULT 1,
                            "include_lower"	BOOLEAN DEFAULT 1,
                            "include_num"	BOOLEAN DEFAULT 1,
                            "include_special"	BOOLEAN DEFAULT 1,
                            "special_allowed"	TEXT DEFAULT "-_!@#$%^&*/|",
                            "can_start_with_upper"	BOOLEAN DEFAULT 1,
                            "can_start_with_lower"	BOOLEAN DEFAULT 1,
                            "can_start_with_num"	BOOLEAN DEFAULT 1,
                            "can_start_with_special"	BOOLEAN DEFAULT 1,
                            "special_allowed_start"	TEXT DEFAULT "-_!@#$%^&*/|",
                            PRIMARY KEY("preferences_id" AUTOINCREMENT)
                        )""")

        # create USER_SITE table
        self.cur.execute("""CREATE TABLE "USER_SITE" (
                            "user_id"	INTEGER NOT NULL,
                            "site_id" INTEGER NOT NULL,
                            "site_url"	BLOB NOT NULL,
                            "site_username"	BLOB NOT NULL,
                            "site_password"	BLOB NOT NULL,
                            "preference_id"	INTEGER,
                            "is_deleted" BOOLEAN DEFAULT 0,
                            PRIMARY KEY("user_id","site_id"),
                            FOREIGN KEY("preference_id") REFERENCES "PASSWORD_PREFERENCES"("preferences_id"),
                            FOREIGN KEY("user_id") REFERENCES "USERS"("user_id")
                        )""")
        
        # create SECURITY_QUESTIONS table
        self.cur.execute("""CREATE TABLE "SECURITY_QUESTIONS" (
                            "question_id" INTEGER NOT NULL,
                            "question" TEXT NOT NULL,
                            PRIMARY KEY("question_id" AUTOINCREMENT)
                         )""")
        
        for question in SECURITY_QUESTIONS_LIST:
            self.cur.execute("""INSERT INTO SECURITY_QUESTIONS (question) VALUES(?)""", (question, ))

        self.conn.commit()

    def derive_key(self, password, salt):
        """Receives a password and a salt, and derives a 32-byte encryption key using PBKDF2 with SHA256."""
        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,
            salt = salt,
            iterations = 600000,
        )
        return kdf.derive(password)
    
    def encrypt_data(self, user_id, data):
        """Receives a user_id and a list of data items, and returns a list of the data items encrypted using the user's DK."""
        self.cur.execute("""SELECT user_dk FROM USERS WHERE user_id = ?""", (user_id, ))
        encrypted_dk = self.cur.fetchone()[0]
        dk_encryption_key = self.get_dk_encryption_key(user_id)
        f = Fernet(dk_encryption_key)
        dk = f.decrypt(encrypted_dk)
        data_f = Fernet(dk)
        encrypted_data = []
        for i in data:
            if type(i) != bytes:
                i = i.encode()
            encrypted_data.append(data_f.encrypt(i))
        return encrypted_data
    
    def decrypt_data(self, user_id, data):
        """Receives a user_id and a list of encrypted data items, and returns a list of the data items decrypted using the user's DK."""
        self.cur.execute("""SELECT user_dk FROM USERS WHERE user_id = ?""", (user_id, ))
        encrypted_dk = self.cur.fetchone()[0]
        dk_encryption_key = self.get_dk_encryption_key(user_id)
        f = Fernet(dk_encryption_key)
        dk = f.decrypt(encrypted_dk)
        data_f = Fernet(dk)
        decrypted_data = []
        for i in data:
            try:
                decrypted_data.append(data_f.decrypt(i).decode())
            except:
                decrypted_data.append(data_f.decrypt(i))
        return decrypted_data
    
    def create_dk_encryption_key(self, username, password_hex, key_salt):
        """Receives a username, password hex and key salt, and returns a DK encryption key derived from them."""
        raw_key = self.derive_key((username + password_hex).encode(), key_salt)
        dk_encryption_key = base64.urlsafe_b64encode(raw_key)
        return dk_encryption_key
    
    def get_dk_encryption_key(self, user_id):
        """Receives a user_id and returns their DK encryption key.\n
        If the key is not found in the users_keys dictionary, derives it from the database and saves it."""
        dk_encryption_key = self.users_keys.get(user_id)
        if dk_encryption_key is None:
            self.cur.execute("""SELECT username, password, key_salt FROM USERS WHERE user_id = ?""", (user_id, ))
            username, password_hex, key_salt = self.cur.fetchone()
            dk_encryption_key = self.create_dk_encryption_key(username, password_hex, key_salt)
            self.users_keys[user_id] = dk_encryption_key
        return dk_encryption_key


    def user_signup(self, username, password, email, phone_number, voice_signature, face_encoding, questions_dict):
        """Receives user signup data, and saves the user in the database.\n
        Hashes the password with a random salt, generates a DK, encrypts all sensitive user data with the DK,
        encrypts the DK with a key derived from the username and password, and inserts the user into the database.\n
        Returns the user_id if successful, None otherwise."""
        try:
            random_password_salt = os.urandom(32)
            salted_password = random_password_salt + password.encode()
            hashed_password = hashlib.sha256(salted_password)
            password_hex = hashed_password.hexdigest()

            user_dk = Fernet.generate_key()
            dk_f = Fernet(user_dk)
            encrypted_email = dk_f.encrypt(email.encode())
            encrypted_phone_number = dk_f.encrypt(phone_number.encode())

            if voice_signature:
                encrypted_voice_signature = dk_f.encrypt(voice_signature)
            else:
                encrypted_voice_signature = None

            if face_encoding:
                encrypted_face_encoding = dk_f.encrypt(face_encoding)
            else:
                encrypted_face_encoding = None

            random_key_salt = os.urandom(16)
            dk_encryption_key = self.create_dk_encryption_key(username, password_hex, random_key_salt)
            
            f = Fernet(dk_encryption_key)
            encrypted_user_dk = f.encrypt(user_dk)

            q_id_1, q_id_2, q_id_3 = questions_dict.keys()
            answer_1 = questions_dict[q_id_1]
            answer_2 = questions_dict[q_id_2]
            answer_3 = questions_dict[q_id_3]
            answers_salt = os.urandom(32)
            hashed_answer_1 = hashlib.sha256(answer_1.encode() + answers_salt).hexdigest()
            hashed_answer_2 = hashlib.sha256(answer_2.encode() + answers_salt).hexdigest()
            hashed_answer_3 = hashlib.sha256(answer_3.encode() + answers_salt).hexdigest()
            self.cur.execute("""INSERT INTO USERS 
                             (username, password, password_salt, email, phone_number, user_dk, key_salt, voice_signature, face_encoding,
                             question_id_1, answer_1, question_id_2, answer_2, question_id_3, answer_3, answers_salt)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                            (username, password_hex, random_password_salt, encrypted_email, encrypted_phone_number, encrypted_user_dk, random_key_salt, encrypted_voice_signature,
                             encrypted_face_encoding, q_id_1, hashed_answer_1, q_id_2, hashed_answer_2, q_id_3, hashed_answer_3, answers_salt))
        except sqlite3.IntegrityError as e:
            return None
        except AttributeError as e:
            return None
        
        user_id = self.cur.lastrowid

        self.conn.commit()

        self.users_keys[user_id] = dk_encryption_key
        return user_id
    
    def does_user_exist(self, username):
        """Receives a username and returns True if the user exists in the database, False otherwise."""
        self.cur.execute("""SELECT EXISTS(SELECT 1 FROM USERS WHERE username = ? LIMIT 1)""", (username, ))
        result = bool(self.cur.fetchone()[0])
        return result

    
    def user_login(self, username, password):
        """Receives a username and password, and verifies the credentials.\n
        Hashes the received password with the stored salt and compares it to the stored hash.\n
        Returns the user_id if the credentials are correct, None otherwise."""
        self.cur.execute("""SELECT password, user_id, password_salt, key_salt FROM USERS WHERE username = ?""", (username, ))
        user_password, user_id, password_salt, key_salt = self.cur.fetchone()

        try:
            salted_password = password_salt + password.encode()
            hashed_password = hashlib.sha256(salted_password)
            password_hex = hashed_password.hexdigest()
        except AttributeError as e:
            return None
        

        if user_password == password_hex:
            dk_encryption_key = self.create_dk_encryption_key(username, password_hex, key_salt)
            self.users_keys[user_id] = dk_encryption_key
            return user_id
        
        return None

    def get_user_email(self, username):
        """Receives a username and returns the user's decrypted email address."""
        self.cur.execute("""SELECT user_id, email FROM USERS WHERE username = ?""", (username, ))
        user_id, email = self.cur.fetchone()
        decrypted_email = self.decrypt_data(user_id, [email])[0]
        return decrypted_email
    
    def get_user_phone_number(self, username):
        """Receives a username and returns the user's decrypted phone number."""
        self.cur.execute("""SELECT user_id, phone_number FROM USERS WHERE username = ?""", (username, ))
        user_id, phone_num = self.cur.fetchone()
        decrypted_phone_num = self.decrypt_data(user_id, [phone_num])[0]
        return decrypted_phone_num
    
    def get_voice_signature(self, username):
        """Receives a username and returns the user's decrypted voice signature. Returns None if no voice signature is stored."""
        self.cur.execute("""SELECT user_id, voice_signature FROM USERS WHERE username = ?""", (username, ))
        user_id, voice_signature = self.cur.fetchone()
        if voice_signature is None:
            return None
        decrypted_voice_signature = self.decrypt_data(user_id, [voice_signature])[0]
        return decrypted_voice_signature
    
    def get_face_encoding(self, username):
        """Receives a username and returns the user's decrypted face encoding. Returns None if no face encoding is stored."""
        self.cur.execute("""SELECT user_id, face_encoding FROM USERS WHERE username = ?""", (username, ))
        user_id, face_encoding = self.cur.fetchone()
        if face_encoding is None:
            return None
        decrypted_face_encoding = self.decrypt_data(user_id, [face_encoding])[0]
        return decrypted_face_encoding
    
    def get_user_auth_options(self, username):
        """Receives a username and returns a dictionary of the authentication options available to them."""
        auth_options = {}
        if self.get_voice_signature(username):
            auth_options["voice_auth"] = True
        else:
            auth_options["voice_auth"] = False
        
        if self.get_face_encoding(username):
            auth_options["face_auth"] = True
        else:
            auth_options["face_auth"] = False

        return auth_options
    
    def setup_voice_auth(self, user_id, voice_signature):
        """Receives a user_id and a voice signature, encrypts the voice signature and stores it in the database."""
        encrypted_voice_signature = self.encrypt_data(user_id, [voice_signature])[0]
        self.cur.execute("""UPDATE USERS
                         SET voice_signature = ?
                         WHERE user_id = ?""",
                         (encrypted_voice_signature, user_id))
        
        self.conn.commit()

    def setup_face_recognition(self, user_id, face_encoding):
        """Receives a user_id and a face encoding, encrypts the face encoding and stores it in the database."""
        encrypted_face_encoding = self.encrypt_data(user_id, [face_encoding])[0]
        self.cur.execute("""UPDATE USERS
                         SET face_encoding = ?
                         WHERE user_id = ?""",
                         (encrypted_face_encoding, user_id))
        
        self.conn.commit()
    
    def get_security_questions_list(self):
        """Returns a list of all security questions from the database."""
        self.cur.execute("""SELECT question FROM SECURITY_QUESTIONS""")
        security_questions_list = [i[0] for i in self.cur.fetchall()]
        return security_questions_list
    
    def get_user_security_questions(self, username):
        """Receives a username and returns a list of the 3 security questions the user chose."""
        self.cur.execute("""SELECT question_id_1, question_id_2, question_id_3 FROM USERS WHERE username = ?""", (username, ))
        q_id_1, q_id_2, q_id_3 = self.cur.fetchone()
        self.cur.execute("""SELECT question FROM SECURITY_QUESTIONS WHERE question_id IN (?,?,?)""", (q_id_1, q_id_2, q_id_3))
        user_questions_list = [row[0] for row in self.cur.fetchall()]
        return user_questions_list
    

    def check_user_security_answers(self, username, answers_list):
        """Receives a username and a list of answers, hashes each answer with the stored salt
        and compares them to the stored hashes. Returns True if all answers are correct, False otherwise."""
        self.cur.execute("""SELECT answer_1, answer_2, answer_3, answers_salt FROM USERS WHERE username = ?""", (username, ))
        *user_answers_list, answers_salt = self.cur.fetchone()
        for i in range(len(user_answers_list)):
            answer = answers_list[i]
            hashed_answer = hashlib.sha256(answer.encode() + answers_salt).hexdigest()
            if hashed_answer != user_answers_list[i]:
                return False
        return True


    def reset_user_password(self, username, new_password):
        """Receives a username and a new password, and resets the user's password.\n
        Decrypts the user's DK with the old DK encryption key, hashes the new password,
        derives a new DK encryption key and re-encrypts the DK with it.\n
        Returns the user_id."""
        self.cur.execute("""SELECT password, password_salt, user_id, key_salt, user_dk FROM USERS WHERE username = ?""", (username, ))
        user_password, password_salt, user_id, key_salt, user_dk = self.cur.fetchone()

        dk_encryption_key = self.create_dk_encryption_key(username, user_password, key_salt)

        f = Fernet(dk_encryption_key)
        decrypted_user_dk = f.decrypt(user_dk)


        new_salted_password = password_salt + new_password.encode()
        new_hashed_password = hashlib.sha256(new_salted_password)
        new_password_hex = new_hashed_password.hexdigest()

        new_dk_encryption_key = self.create_dk_encryption_key(username, new_password_hex, key_salt)

        new_f = Fernet(new_dk_encryption_key)
        reencrypted_user_dk = new_f.encrypt(decrypted_user_dk)

        self.cur.execute("""UPDATE USERS
                         SET password = ?, user_dk = ?
                         WHERE user_id = ?""",
                         (new_password_hex, reencrypted_user_dk, user_id))
        
        self.conn.commit()
        
        self.users_keys[user_id] = new_dk_encryption_key

        return user_id


    def does_site_exist(self, user_id, site_url):
        """Receives a user_id and a site URL, and returns True if the site exists and is not deleted, False otherwise."""
        registered_sites = self.get_registered_sites(user_id, False)
        return site_url in registered_sites

    def does_deleted_site_exist(self, user_id, site_url):
        """Receives a user_id and a site URL, and returns True if the site exists and is deleted, False otherwise."""
        registered_sites = self.get_registered_sites(user_id, True)
        return site_url in registered_sites


    def get_site_id(self, user_id, site_url):
        """Receives a user_id and a site URL, and returns the site_id by decrypting and comparing site URLs. Returns None if not found."""
        self.cur.execute("""SELECT site_id, site_url FROM USER_SITE WHERE user_id = ?""", (user_id, ))
        lst = self.cur.fetchall()
        for i in lst:
            encrypted_site_url = i[1]
            if self.decrypt_data(user_id, [encrypted_site_url])[0] == site_url:
                return i[0]
        return None

    def count_registered_sites(self, user_id):
        """Receives a user_id and returns the number of sites registered to the user."""
        self.cur.execute("""SELECT COUNT(*) FROM USER_SITE WHERE user_id = ?""", (user_id, ))
        count = self.cur.fetchone()[0]
        return count
    
    def set_default_password_preferences(self):
        """Inserts a new row with default password preferences into the PASSWORD_PREFERENCES table and returns its ID."""
        self.cur.execute("""INSERT INTO PASSWORD_PREFERENCES DEFAULT VALUES""")
        preference_id = self.cur.lastrowid
        self.conn.commit()
        return preference_id

    def update_password_preferences(self, user_id, site_url, preferences):
        """Receives a user_id, site URL and a preferences dictionary, and updates the password preferences for the site."""
        site_id = self.get_site_id(user_id, site_url)
        preference_id = self.get_preference_id(user_id, site_id)
        max_length = preferences["max_length"]
        include = preferences["include"]
        special_allowed = preferences["special_allowed"]
        start = preferences["start"]
        special_allowed_start = preferences["special_allowed_start"]
        self.cur.execute("""UPDATE PASSWORD_PREFERENCES
                         SET max_length = ?, include_upper = ?, include_lower = ?, include_num = ?, include_special = ?, special_allowed = ?,
                         can_start_with_upper = ?, can_start_with_lower = ?, can_start_with_num = ?, can_start_with_special = ?, special_allowed_start = ?
                         WHERE preferences_id = ?""",
                         (max_length, include["Upper"], include["Lower"], include["Number"], include["Special"], special_allowed,
                         start["Upper"], start["Lower"], start["Number"], start["Special"], special_allowed_start, preference_id))

        self.conn.commit()

    def get_password_preferences(self, user_id, site_url):
        """Receives a user_id and a site URL, and returns a dictionary of the password preferences for the site."""
        site_id = self.get_site_id(user_id, site_url)
        preference_id = self.get_preference_id(user_id, site_id)
        self.cur.execute("""SELECT max_length, include_upper, include_lower, include_num, include_special, special_allowed,
                         can_start_with_upper, can_start_with_lower, can_start_with_num, can_start_with_special, special_allowed_start
                         FROM PASSWORD_PREFERENCES WHERE preferences_id = ?""",
                         (preference_id, ))
        
        preferences_lst = self.cur.fetchone()
        preferences = {}
        preferences["max_length"] = preferences_lst[0]
        preferences["include"] = {"Upper" : preferences_lst[1], "Lower" : preferences_lst[2], "Number" : preferences_lst[3], "Special" : preferences_lst[4]}
        preferences["special_allowed"] = preferences_lst[5]
        preferences["start"] = {"Upper" : preferences_lst[6], "Lower" : preferences_lst[7], "Number" : preferences_lst[8], "Special" : preferences_lst[9]}
        preferences["special_allowed_start"] = preferences_lst[10]
        return preferences


    def register_site(self, user_id, site_url, site_username, site_password, password_preferences = None):
        """Receives a user_id, site URL, site username, site password and optional password preferences,
        encrypts the site data and inserts it into the database with default password preferences.
        If custom password preferences are provided, updates them after insertion."""
        site_id = self.count_registered_sites(user_id)
        preference_id = self.set_default_password_preferences()
        encrypted_site_url, encrypted_site_username, encrypted_site_password = self.encrypt_data(user_id, [site_url, site_username, site_password])
        self.cur.execute("""INSERT INTO USER_SITE (user_id, site_id, site_url, site_username, site_password, preference_id)
                        VALUES(?,?,?,?,?,?)""",
                        (user_id, site_id, encrypted_site_url, encrypted_site_username, encrypted_site_password, preference_id))
        
        if password_preferences is not None:
            self.update_password_preferences(user_id, site_url, password_preferences)

        self.conn.commit()

    def get_preference_id(self, user_id, site_id):
        """Receives a user_id and a site_id, and returns the preference_id for the site."""
        self.cur.execute("""SELECT preference_id FROM USER_SITE WHERE user_id = ? AND site_id = ?""",
                         (user_id, site_id))
        preference_id = self.cur.fetchone()[0]
        return preference_id

    def change_site_password(self, user_id, site_url, new_site_password):
        """Receives a user_id, site URL and a new password, encrypts the new password and updates it in the database."""
        site_id = self.get_site_id(user_id, site_url)
        encrypted_site_password = self.encrypt_data(user_id, [new_site_password])[0]
        self.cur.execute("""UPDATE USER_SITE
                         SET site_password = ?
                         WHERE user_id = ? AND site_id = ?""",
                         (encrypted_site_password, user_id, site_id))

        self.conn.commit()

    
    def get_registered_sites(self, user_id, get_deleted):
        """Receives a user_id and a boolean, and returns a decrypted list of the user's registered site URLs.\n
        If get_deleted is True, returns the deleted sites. Otherwise, returns the active sites."""
        self.cur.execute("""SELECT site_url FROM USER_SITE WHERE user_id = ? AND is_deleted = ?""", (user_id, int(get_deleted)))

        lst = self.cur.fetchall()
        sites = [i[0] for i in lst]

        decrypted_sites = self.decrypt_data(user_id, sites)
        return decrypted_sites
    
    def get_site_info(self, user_id, site_url):
        """Receives a user_id and a site URL, and returns the decrypted site username and site password."""
        site_id = self.get_site_id(user_id, site_url)
        self.cur.execute("""SELECT site_username, site_password FROM USER_SITE WHERE user_id = ? AND site_id = ?""", 
                         (user_id, site_id))

        site_info = self.cur.fetchone()
        decrypted_site_info = self.decrypt_data(user_id, site_info)
        return decrypted_site_info
    
    def delete_site(self, user_id, site_url):
        """Receives a user_id and a site URL, and marks the site as deleted in the database."""
        site_id = self.get_site_id(user_id, site_url)
        self.cur.execute("""UPDATE USER_SITE
                         SET is_deleted = 1
                         WHERE user_id = ? AND site_id = ?""",
                         (user_id, site_id))
        
        self.conn.commit()

    def recover_site(self, user_id, site_url):
        """Receives a user_id and a site URL, and marks the previously deleted site as active in the database."""
        site_id = self.get_site_id(user_id, site_url)
        self.cur.execute("""UPDATE USER_SITE
                         SET is_deleted = 0
                         WHERE user_id = ? AND site_id = ?""",
                         (user_id, site_id))
        
        self.conn.commit()

