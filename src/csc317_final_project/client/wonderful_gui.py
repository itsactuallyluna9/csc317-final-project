import threading

class GUI:

    def __init__(self):
        self._username = None
        self._password = None
        self._login_flag = threading.Event()
        self._registration_flag = threading.Event()
        self._user_flag = threading.Event()
        self._home_flag = threading.Event()

    @property
    def login_flag(self):
        return self._login_flag
    
    @property
    def user_flag(self):
        return self._user_flag
    
    @property
    def home_flag(self):
        return self._home_flag
    
    @property
    def registration_flag(self):
        return self._registration_flag
    
    @property
    def username(self):
        return self._username
    
    @property
    def password(self):
        return self._password


    def run_gui(self):
        #load the gui here
        while True:
            #some main event loop
            self.login()
            pass
        pass

    def login(self):
        self._username = any() #grab the username from the gui
        self._password = any() #grab the password from the gui
        self._login_flag.set() 


