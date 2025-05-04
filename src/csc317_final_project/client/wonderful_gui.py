import threading
import sys
from PySide6 import QtCore, QtWidgets, QtGui

class GUI(QtWidgets.QWidget):

    def __init__(self, user_list):
        super().__init__()

        self._login_page = self.Login_GUI()
        self._user_page = self.User_Page_GUI(user_list)

        self._user_flag = threading.Event()
        self._home_flag = threading.Event()
        self._video_flag = threading.Event()
        self._page_flag = threading.Event()
        self._back_flag = threading.Event()
        self._login_flag = self._login_page.login_flag
        self._registration_flag = self._login_page.registration_flag

        self._layout = QtWidgets.QStackedLayout(self)
        self._layout.addWidget(self._login_page)
        self._layout.addWidget(self._user_page)
        self._server_response = {}


    @property
    def server_response(self):
        return self._server_response
    
    @server_response.setter
    def server_response(self, v):
        self._server_response = v

    @property
    def page_flag(self):
            return self._page_flag
    
    @page_flag.setter
    def page_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._page_flag.set()

        else:
            self._page_flag.clear()
    
    @property
    def login_flag(self):
            return self._login_flag
    
    @login_flag.setter
    def login_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._login_flag.set()

        else:
            self._login_flag.clear()
    
    @property
    def registration_flag(self):
            return self._registration_flag
    
    @registration_flag.setter
    def registration_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._registration_flag.set()

        else:
            self._registration_flag.clear()
    
    @property
    def user_flag(self):
            return self._user_flag
    
    @user_flag.setter
    def user_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._user_flag.set()

        else:
            self._user_flag.clear()
        
    @property
    def video_flag(self):
            return self._video_flag
    
    @video_flag.setter
    def video_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._video_flag.set()

        else:
            self._video_flag.clear()
    
    @property
    def home_flag(self):
            return self._home_flag
    
    @home_flag.setter
    def home_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._home_flag.set()

        else:
            self._home_flag.clear()
    
    @property
    def back_flag(self):
            return self._back_flag
    
    @back_flag.setter
    def back_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._back_flag.set()

        else:
            self._back_flag.clear()
    

    class Login_GUI(QtWidgets.QWidget):

        def __init__(self):
            super().__init__()
            self._username = None
            self._password = None
            self._login_flag = threading.Event()
            self._registration_flag = threading.Event()

            self._login_button = QtWidgets.QPushButton("Login")
            self._login_button.setFixedWidth(100)
            self._text = QtWidgets.QLabel("Login or Register", alignment=QtCore.Qt.AlignHCenter)
            self._text.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
            self._registration_button = QtWidgets.QPushButton("Register")
            self._registration_button.setFixedWidth(100)
            self._username_entry = QtWidgets.QLineEdit("Username")
            self._username_entry.setFixedWidth(200)
            self._password_entry = QtWidgets.QLineEdit("Password")
            self._password_entry.setFixedWidth(200)

            self._layout = QtWidgets.QVBoxLayout(self)
            self._buttons_layout = QtWidgets.QHBoxLayout()
            self._layout.addWidget(self._text)
            self._layout.addWidget(self._username_entry, alignment=QtCore.Qt.AlignHCenter)
            self._layout.addWidget(self._password_entry, alignment=QtCore.Qt.AlignHCenter)
            self._buttons_layout.addWidget(self._login_button, alignment=QtCore.Qt.AlignVCenter)
            self._buttons_layout.addWidget(self._registration_button, alignment=QtCore.Qt.AlignVCenter)
            self._layout.addLayout(self._buttons_layout)


            self._login_button.clicked.connect(self._login)
            self._registration_button.clicked.connect(self._register)

        @property
        def login_flag(self):
            return self._login_flag
        
        @login_flag.setter
        def login_flag(self, v):
            if not isinstance(v, bool):
                raise TypeError
            
            if v:
                self._login_flag.set()

            else:
                self._login_flag.clear()
        
        @property
        def registration_flag(self):
            return self._registration_flag
        
        @registration_flag.setter
        def registration_flag(self, v):
            if not isinstance(v, bool):
                raise TypeError
            
            if v:
                self._registration_flag.set()

            else:
                self._registration_flag.clear()
        
        @property
        def username(self):
            return self._username
        
        @property
        def password(self):
            return self._password
        
        
        @QtCore.Slot()
        def _login(self):
            self._username = self._username_entry.text()
            self._password = self._password_entry.text()
            self._login_flag.set()
        
        @QtCore.Slot()
        def _register(self):
            self._username = self._username_entry.text()
            self._password = self._password_entry.text()
            self._registration_flag.set()
    

    class User_Page_GUI(QtWidgets.QWidget):

        def __init__(self, user_list):
            super().__init__()

            self._user_list = user_list

            self._layout = QtWidgets.QGridLayout(self)

            for user in user_list:
                user_button = QtWidgets.QPushButton(f"{user}")
                self._layout.addWidget(user_button)
            


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    button = GUI(["Someone", "Someone_else", "A_third_person"])
    button.resize(800, 600)
    button.show()

    sys.exit(app.exec())
