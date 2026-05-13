import datetime


MAX_FAILED_LOGIN_ATTEMPTS_ALLOWED = 5
FAILED_LOGIN_ATTEMPTS_MINUTES_WINDOW = 1
TIMEOUT_LENGTH_MINUTES = 2


class UserManager:

    def __init__(self):
        self.logged_users = {}    # dictionary matching client sockets to their user_id
        self.user_login_attempts = {}    # dictionary matching usernames to a list of their failed login attempt times
        self.users_in_timeout = {}    # dictionary matching usernames to the time they entered timeout


    def is_user_in_timeout(self, username):
        """Receives a username and returns True if the user is currently in timeout, False otherwise.\n
        If the timeout has expired, removes the user from the timeout dictionary."""
        if username in self.users_in_timeout.keys():
            timeout_entry_time = self.users_in_timeout[username]
            current_time = datetime.datetime.now()
            time_diff = current_time - timeout_entry_time
            if time_diff > datetime.timedelta(minutes = TIMEOUT_LENGTH_MINUTES):
                self.users_in_timeout.pop(username)
                return False
            else:
                return True
        else:
            return False

    def register_failed_login_attempt(self, username):
        """registers the time of the failed login attempt of the user and return whether or not the user has exceeded 
        the max ammount of failed attempts allowed in a certain amount of time"""

        current_time = datetime.datetime.now()
        if username not in self.user_login_attempts.keys():
            self.user_login_attempts[username] = [current_time]
            return False
        else:
            attempts_list = self.user_login_attempts[username]
            failed_login_attempts_count = 1
            for i in range(len(attempts_list) - 1, -1, -1):
                login_time = attempts_list[i]
                time_diff = current_time - login_time
                if time_diff > datetime.timedelta(minutes = FAILED_LOGIN_ATTEMPTS_MINUTES_WINDOW):
                    attempts_list.append(current_time)
                    self.user_login_attempts[username] = attempts_list[i + 1::]
                    return False
                else:
                    failed_login_attempts_count += 1
                    if failed_login_attempts_count > MAX_FAILED_LOGIN_ATTEMPTS_ALLOWED:
                        self.users_in_timeout[username] = current_time
                        return True
                    
            self.user_login_attempts[username].append(current_time)
            return False
        
    def successful_login_attempt(self, username):
        """Receives a username and clears their failed login attempts history."""
        if username in self.user_login_attempts.keys():
            self.user_login_attempts.pop(username)
