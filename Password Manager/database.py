import sqlite3
import os
import hashlib

DB_PATH = r"C:\Users\noams\OneDrive\Databases\PasswordManager.db"

class DataBase:

    def __init__(self):
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
                            email TEXT NOT NULL UNIQUE,
                            phone_number TEXT NOT NULL UNIQUE,
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
                            "site_url"	TEXT NOT NULL,
                            "site_username"	TEXT NOT NULL,
                            "site_password"	TEXT NOT NULL,
                            "preference_id"	INTEGER,
                            PRIMARY KEY("user_id","site_url"),
                            FOREIGN KEY("preference_id") REFERENCES "PASSWORD_PREFERENCES"("preferences_id"),
                            FOREIGN KEY("user_id") REFERENCES "USERS"("user_id")
                        )""")

        self.conn.commit()

    def user_signup(self, username, password, email, phone_number):
        try:
            password_data = password.encode()
            hashed_password = hashlib.sha256(password_data)
            password_hex = hashed_password.hexdigest()
            self.cur.execute("""INSERT INTO USERS (username, password, email, phone_number)
                            VALUES(?,?,?,?)""", 
                            (username, password_hex, email, phone_number))
        except sqlite3.IntegrityError as e:
            return None
        except AttributeError as e:
            return None
        
        user_id = self.cur.lastrowid

        self.conn.commit()

        return user_id
    
    def does_user_exist(self, username):
        self.cur.execute("""SELECT EXISTS(SELECT 1 FROM USERS WHERE username = ? LIMIT 1)""", (username, ))
        result = bool(self.cur.fetchone()[0])
        return result
    
    def user_login(self, username, password):
        self.cur.execute("""SELECT password, user_id FROM USERS WHERE username = ?""", (username, ))

        try:
            password_data = password.encode()
            hashed_password = hashlib.sha256(password_data)
            password_hex = hashed_password.hexdigest()
        except AttributeError as e:
            return None
        
        user_password, user_id = self.cur.fetchone()
        if user_password == password_hex:
            return user_id
        
        return None

    def does_site_exist(self, user_id, site_url):
        self.cur.execute("""SELECT EXISTS(SELECT 1 FROM USER_SITE WHERE user_id = ? AND site_url = ? LIMIT 1)""",
                         (user_id, site_url))
        result = bool(self.cur.fetchone()[0])
        return result

    def register_site(self, user_id, site_url, site_username, site_password):
        self.cur.execute("""INSERT INTO USER_SITE (user_id, site_url, site_username, site_password, preference_id)
                        VALUES(?,?,?,?,?)""",
                        (user_id, site_url, site_username, site_password, None))

        self.conn.commit()


    def change_site_password(self, user_id, site_url, new_site_password):
        self.cur.execute("""UPDATE USER_SITE
                         SET site_password = ?
                         WHERE user_id = ? AND site_url = ?""",
                         (new_site_password, user_id, site_url))

        self.conn.commit()

    
    def get_registered_sites(self, user_id):
        self.cur.execute("""SELECT site_url FROM USER_SITE WHERE user_id = ?""", (user_id, ))

        lst = self.cur.fetchall()
        sites = [i[0] for i in lst]

        return sites
    
    def get_site_info(self, user_id, site_url):
        self.cur.execute("""SELECT site_username, site_password FROM USER_SITE WHERE user_id = ? AND site_url = ?""", (user_id, site_url))

        return self.cur.fetchone()
    
    
    

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