import threading
import sys
from PySide6 import QtCore, QtWidgets, QtGui

class GUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self._login_page = self.Login_GUI(self)

        self._upload_file_path = None

        self._author_folder = None

        self._current_page = None

        self._user_flag = threading.Event()
        self._home_flag = threading.Event()
        self._video_flag = threading.Event()
        self._page_flag = threading.Event()
        self._back_flag = threading.Event()
        self._login_success = threading.Event()
        self._login_failure = threading.Event()
        self._upload_flag = threading.Event()
        self._response_flag = threading.Event()
        self._login_flag = self._login_page.login_flag
        self._registration_flag = self._login_page.registration_flag

        self._layout = QtWidgets.QStackedLayout(self)
        self._layout.addWidget(self._login_page)
        self._server_response = {}
    
    def create_user_page(self, user_list, current_page, max_page):
        self._user_page = self.User_Page_GUI(user_list, current_page, max_page, self)
        self._layout.addWidget(self._user_page)
        self._layout.setCurrentWidget(self._user_page)

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
    
    @property
    def login_success(self):
            return self._login_success
    
    @login_success.setter
    def login_success(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._login_success.set()

        else:
            self._login_success.clear()
    
    @property
    def login_failure(self):
            return self._login_failure
    
    
    @login_failure.setter
    def login_failure(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._login_failure.set()

        else:
            self._login_failure.clear()
    
    @property
    def upload_flag(self):
            return self._upload_flag
        
    @upload_flag.setter
    def upload_flag(self, v):
        if not isinstance(v, bool):
            raise TypeError
        if v:
            self._upload_flag.set()

        else:
            self._upload_flag.clear()
    
    @property
    def response_flag(self):
            return self._response_flag
    
    @response_flag.setter
    def response_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._response_flag.set()

        else:
            self._response_flag.clear()
        
    @property
    def login_page(self):
        return self._login_page
    
    @property
    def user_page(self):
        return self._user_page
    
    @property
    def layout(self):
        return self._layout
    
    @property
    def upload_file_path(self):
        return self._upload_file_path
    
    @property
    def current_page(self):
        return self._current_page
    
    @current_page.setter
    def current_page(self, v):
        if not isinstance(v, int):
            raise TypeError
        self._current_page = v

    
    class Login_GUI(QtWidgets.QWidget):

        def __init__(self, mainGUI):
            super().__init__()
            self._mainGUI = mainGUI
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
            while True:
                if self._mainGUI.login_success.is_set():
                    sr = self._mainGUI.server_response
                    self._mainGUI.create_user_page(sr["result"], sr["current_page"], sr["max_page"])
                    self._mainGUI.login_success = False
                    self._mainGUI.current_page = 0
                    break
                elif self._mainGUI.login_failure.is_set():
                    #tell user
                    self._mainGUI.login_failure = False
                    break
            self._mainGUI.layout.setCurrentIndex(1)

        
        @QtCore.Slot()
        def _register(self):
            self._username = self._username_entry.text()
            self._password = self._password_entry.text()
            self._registration_flag.set()
    

    class User_Page_GUI(QtWidgets.QWidget):

        def __init__(self, user_list, current_page, max_page, mainGUI):
            super().__init__()

            self._mainGUI = mainGUI
            self._user_list = user_list
            self._current_page = current_page
            self._max_page = max_page

            self._grid = QtWidgets.QGridLayout(self)
            row_value = 1
            column_value = 0
            for user in user_list:
                user_button = QtWidgets.QPushButton(f"{user}", self)
                user_button.setFixedSize(100, 100)
                user_button.clicked.connect(self._folder_clicked)
                self._grid.addWidget(user_button, row_value, column_value, alignment=QtCore.Qt.AlignTop)
                if column_value == 4:
                    column_value = 0
                    row_value += 1
                else:
                    column_value += 1
            self._back = QtWidgets.QPushButton("<-", self)
            self._back.setFixedSize(50, 35)
            self._forward = QtWidgets.QPushButton("->", self)
            self._forward.setFixedSize(50, 35)
            self._title = QtWidgets.QLabel("Users", alignment=QtCore.Qt.AlignTop)
            self._title.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
            self._home = QtWidgets.QPushButton("HOME", self)
            self._home.setFixedSize(50, 35)
            self._back_real = QtWidgets.QPushButton("BACK", self)
            self._back_real.setFixedSize(50, 35)
            self._upload = QtWidgets.QPushButton("UPLOAD", self)
            self._upload.setFixedSize(75, 35)
            self._upload.clicked.connect(self._upload_clicked)
            self._grid.addWidget(self._back_real, 0, 1, alignment=QtCore.Qt.AlignTop)
            self._grid.addWidget(self._home, 0, 2, alignment=QtCore.Qt.AlignTop)
            self._grid.addWidget(self._upload, 0, 3, alignment=QtCore.Qt.AlignTop)
            self._grid.addWidget(self._title, 0, 0, alignment=QtCore.Qt.AlignTop)
            self._grid.addWidget(self._back, row_value + 1, 0, alignment=QtCore.Qt.AlignLeft)
            self._grid.addWidget(self._forward, row_value + 1, 1, alignment=QtCore.Qt.AlignLeft)

        @QtCore.Slot()
        def _folder_clicked(self):
            folder = self.sender()

            print(folder.text())

        @QtCore.Slot()
        def _back_real_clicked(self):
            pass
        
        @QtCore.Slot()
        def _home_clicked(self):
            pass

        @QtCore.Slot()
        def _upload_clicked(self):
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '.')
            self._mainGUI._upload_file_path = filename
            self._mainGUI._upload_flag.set()

        @QtCore.Slot()
        def _forward_page_clicked(self):
            if self._mainGUI.current_page == self._max_page:
                return
            self._mainGUI.current_page += 1
            self._mainGUI.page_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_page(self._mainGUI.current_page, self._mainGUI)
                    self._mainGUI.server_response = False
                    break

        @QtCore.Slot()
        def _back_page_clicked(self):
            if self._mainGUI.current_page == 0:
                return
            self._mainGUI.current_page -= 1
            self._mainGUI.page_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_page(self._mainGUI.current_page, self._mainGUI)
                    self._mainGUI.server_response = False
                    break
        
def new_page(page_num, mainGUI):
    sr = mainGUI.server_response
    mainGUI.create_user_page(sr["result"], sr["current_page"], sr["max_page"])
    mainGUI.current_page = page_num
    

def run_gui():
    app = QtWidgets.QApplication([])

    button = GUI()
    button.resize(800, 600)
    button.show()

    sys.exit(app.exec())
