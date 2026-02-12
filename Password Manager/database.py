import sqlite3
import os
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

DB_PATH = r"C:\Users\noams\OneDrive\Databases\PasswordManager.db"

class DataBase:

    def __init__(self):
        self.users_keys = {}

        init_db = False
        if not os.path.exists(DB_PATH):
            init_db = True
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()
        
        if init_db:
            self.init_db()



    def init_db(self):

        # create USERS table
        self.cur.execute("""CREATE TABLE "USERS" (
                            user_id	INTEGER,
                            password TEXT NOT NULL,
                            username TEXT NOT NULL UNIQUE,
                            password_salt BLOB NOT NULL,
                            email BLOB NOT NULL UNIQUE,
                            phone_number BLOB NOT NULL UNIQUE,
                            user_dk BLOB NOT NULL UNIQUE,
                            key_salt BLOB NOT NULL,
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
                            PRIMARY KEY("user_id","site_id"),
                            FOREIGN KEY("preference_id") REFERENCES "PASSWORD_PREFERENCES"("preferences_id"),
                            FOREIGN KEY("user_id") REFERENCES "USERS"("user_id")
                        )""")

        self.conn.commit()

    def derive_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,
            salt = salt,
            iterations = 600000,
        )
        return kdf.derive(password)
    
    def encrypt_data(self, user_id, data):
        self.cur.execute("""SELECT user_dk FROM USERS WHERE user_id = ?""", (user_id, ))
        encrypted_dk = self.cur.fetchone()[0]
        dk_encryption_key = self.users_keys[user_id]
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
        self.cur.execute("""SELECT user_dk FROM USERS WHERE user_id = ?""", (user_id, ))
        encrypted_dk = self.cur.fetchone()[0]
        dk_encryption_key = self.users_keys[user_id]
        f = Fernet(dk_encryption_key)
        dk = f.decrypt(encrypted_dk)
        data_f = Fernet(dk)
        decrypted_data = []
        for i in data:
            decrypted_data.append(data_f.decrypt(i).decode())
        return decrypted_data

    def user_signup(self, username, password, email, phone_number):
        try:
            random_password_salt = os.urandom(32)
            salted_password = random_password_salt + password.encode()
            hashed_password = hashlib.sha256(salted_password)
            password_hex = hashed_password.hexdigest()

            user_dk = Fernet.generate_key()
            dk_f = Fernet(user_dk)
            encrypted_email = dk_f.encrypt(email)
            encrypted_phone_number = dk_f.encrypt(phone_number)

            random_key_salt = os.urandom(16)
            raw_key = self.derive_key((username + password_hex).encode(), random_key_salt)
            dk_encryption_key = base64.urlsafe_b64encode(raw_key)
            f = Fernet(dk_encryption_key)
            encrypted_user_dk = f.encrypt(user_dk)
            self.cur.execute("""INSERT INTO USERS (username, password, password_salt, email, phone_number, user_dk, key_salt)
                            VALUES(?,?,?,?,?,?,?)""", 
                            (username, password_hex, random_password_salt, encrypted_email, encrypted_phone_number, encrypted_user_dk, random_key_salt))
        except sqlite3.IntegrityError as e:
            print(e)
            return None
        except AttributeError as e:
            print(e)
            return None
        
        user_id = self.cur.lastrowid

        self.conn.commit()

        return user_id
    
    def does_user_exist(self, username):
        self.cur.execute("""SELECT EXISTS(SELECT 1 FROM USERS WHERE username = ? LIMIT 1)""", (username, ))
        result = bool(self.cur.fetchone()[0])
        return result
    
    def user_login(self, username, password):
        self.cur.execute("""SELECT password, user_id, password_salt, key_salt FROM USERS WHERE username = ?""", (username, ))
        user_password, user_id, password_salt, key_salt = self.cur.fetchone()

        try:
            salted_password = password_salt + password.encode()
            hashed_password = hashlib.sha256(salted_password)
            password_hex = hashed_password.hexdigest()
        except AttributeError as e:
            return None
        

        if user_password == password_hex:
            raw_key = self.derive_key((username + password_hex).encode(), key_salt)
            dk_encryption_key = base64.urlsafe_b64encode(raw_key)
            self.users_keys[user_id] = dk_encryption_key
            return user_id
        
        return None

    def does_site_exist(self, user_id, site_url):
        registered_sites = self.get_registered_sites(user_id)
        return site_url in registered_sites
        # encrypted_site_url = self.encrypt_data(user_id, [site_url])[0]
        # self.cur.execute("""SELECT EXISTS(SELECT 1 FROM USER_SITE WHERE user_id = ? AND site_url = ? LIMIT 1)""",
        #                  (user_id, encrypted_site_url))
        # result = bool(self.cur.fetchone()[0])
        # return result

    def get_site_id(self, user_id, site_url):
        self.cur.execute("""SELECT site_id, site_url FROM USER_SITE WHERE user_id = ?""", (user_id, ))
        lst = self.cur.fetchall()
        for i in lst:
            encrypted_site_url = i[1]
            if self.decrypt_data(user_id, [encrypted_site_url])[0] == site_url:
                return i[0]
        return None

    def count_registered_sites(self, user_id):
        self.cur.execute("""SELECT COUNT(*) FROM USER_SITE WHERE user_id = ?""", (user_id, ))
        count = self.cur.fetchone()[0]
        return count

    def register_site(self, user_id, site_url, site_username, site_password):
        site_id = self.count_registered_sites(user_id)
        encrypted_site_url, encrypted_site_username, encrypted_site_password = self.encrypt_data(user_id, [site_url, site_username, site_password])
        self.cur.execute("""INSERT INTO USER_SITE (user_id, site_id, site_url, site_username, site_password, preference_id)
                        VALUES(?,?,?,?,?,?)""",
                        (user_id, site_id, encrypted_site_url, encrypted_site_username, encrypted_site_password, None))

        self.conn.commit()


    def change_site_password(self, user_id, site_url, new_site_password):
        site_id = self.get_site_id(user_id, site_url)
        encrypted_site_password = self.encrypt_data(user_id, [new_site_password])[0]
        self.cur.execute("""UPDATE USER_SITE
                         SET site_password = ?
                         WHERE user_id = ? AND site_id = ?""",
                         (encrypted_site_password, user_id, site_id))

        self.conn.commit()

    
    def get_registered_sites(self, user_id):
        self.cur.execute("""SELECT site_url FROM USER_SITE WHERE user_id = ?""", (user_id, ))

        lst = self.cur.fetchall()
        sites = [i[0] for i in lst]

        decrypted_sites = self.decrypt_data(user_id, sites)
        return decrypted_sites
    
    def get_site_info(self, user_id, site_url):
        site_id = self.get_site_id(user_id, site_url)
        self.cur.execute("""SELECT site_username, site_password FROM USER_SITE WHERE user_id = ? AND site_id = ?""", 
                         (user_id, site_id))

        site_info = self.cur.fetchone()
        decrypted_site_info = self.decrypt_data(user_id, site_info)
        return decrypted_site_info

    
    
    

# db = DataBase()
# db.user_signup("noam", "1234", "noam@gmail.com", "054")
# user_id = db.user_login("noam", "1234")
# db.register_site(user_id, "mashov", "noam123", "Abcd123")
# db.register_site(user_id, "whatsapp", "noam456", "Abcd456")
# print(db.get_registered_sites(user_id))
# print(db.get_site_info(user_id, "mashov"))

# if db.does_user_exist("noam2"):
#     user_id = db.user_login("noam2", "")
# else:
#     print("user doesn't exist")