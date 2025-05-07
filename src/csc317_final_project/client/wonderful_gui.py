import threading
import sys
import time
from PySide6 import QtCore, QtWidgets, QtGui, QtMultimedia, QtMultimediaWidgets

SEGMENT_DURATION = 3

class GUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self._login_page = self.Login_GUI(self)
        self._upload_file_path = None
        self._author_folder = None
        self._current_phase = None
        self._current_page = None
        self._video_id = None
        self._segment_num = None
        self._segment_quality = None
        self._current_segment = None
        self._next_segment = None

        self._user_flag = threading.Event()
        self._home_flag = threading.Event()
        self._video_flag = threading.Event()
        self._page_flag = threading.Event()
        self._back_flag = threading.Event()
        self._login_success = threading.Event()
        self._login_failure = threading.Event()
        self._upload_flag = threading.Event()
        self._response_flag = threading.Event()
        self._segment_request_flag = threading.Event()
        self._segment_ready_flag = threading.Event()
        self._login_flag = self._login_page.login_flag
        self._registration_flag = self._login_page.registration_flag

        self._layout = QtWidgets.QStackedLayout(self)
        self._layout.addWidget(self._login_page)
        self._server_response = {}
    
    def create_user_page(self, user_list, current_page, max_page):
        self._user_page = self.User_Page_GUI(user_list, current_page, max_page, self)
        self._layout.addWidget(self._user_page)
        self._layout.setCurrentWidget(self._user_page)
    
    def create_video_page(self, video_list, current_page, max_page, author):
        print("creating video page...")
        self._video_page = self.Video_Page_GUI(video_list, current_page, max_page, self, author)
        self._layout.addWidget(self._video_page)
        self._layout.setCurrentWidget(self._video_page)
        print("video page created...")

    def create_video_player(self):
        self._video_player = self.Video_Outside_GUI(self._server_response, self)
        print("video gui created")
        self._layout.addWidget(self._video_player)
        print("widget filed")
        self._layout.setCurrentWidget(self._video_player)
        print("showing widget...")

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
    def segment_request_flag(self):
            return self._segment_request_flag
    
    @segment_request_flag.setter
    def segment_request_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._segment_request_flag.set()

        else:
            self._segment_request_flag.clear()
    
    @property
    def segment_ready_flag(self):
            return self._segment_ready_flag
    
    @segment_ready_flag.setter
    def segment_ready_flag(self, v):

        if not isinstance(v, bool):
            raise TypeError

        if v:
            self._segment_ready_flag.set()

        else:
            self._segment_ready_flag.clear()
        
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

    @property
    def author_folder(self):
        return self._author_folder
    
    @author_folder.setter
    def author_folder(self, v):
        if not isinstance(v, str):
            raise TypeError
        self._author_folder = v

    @property
    def current_phase(self):
        return self._current_phase
    
    @current_phase.setter
    def current_phase(self, v):
        if not isinstance(v, str):
            raise TypeError
        self._current_phase = v
    
    @property
    def video_id(self):
        return self._video_id
    
    @video_id.setter
    def video_id(self, v):
        if not isinstance(v, int):
            raise TypeError
        self._video_id = v
    
    @property
    def segment_num(self):
        return self._segment_num
    
    @segment_num.setter
    def segment_num(self, v):
        if not isinstance(v, int):
            raise TypeError
        self._segment_num = v
    
    @property
    def segment_quality(self):
        return self._segment_quality
    
    @segment_quality.setter
    def segment_quality(self, v):
        if not isinstance(v, int):
            raise TypeError
        self._segment_quality = v

    @property
    def current_segment(self):
        return self._current_segment
    
    @current_segment.setter
    def current_segment(self, v):
        self._current_segment = v

    @property
    def next_segment(self):
        return self._next_segment
    
    @next_segment.setter
    def next_segment(self, v):
        self._next_segment = v


    
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
                user_button = QtWidgets.QPushButton(f"{user['username']}", self)
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
            self._back.clicked.connect(self._back_page_clicked)
            self._forward = QtWidgets.QPushButton("->", self)
            self._forward.setFixedSize(50, 35)
            self._forward.clicked.connect(self._forward_page_clicked)
            self._title = QtWidgets.QLabel("Users", alignment=QtCore.Qt.AlignTop)
            self._title.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
            self._home = QtWidgets.QPushButton("HOME", self)
            self._home.setFixedSize(50, 35)
            self._home.clicked.connect(self._home_clicked)
            self._back_real = QtWidgets.QPushButton("BACK", self)
            self._back_real.setFixedSize(50, 35)
            self._back_real.clicked.connect(self._back_real_clicked)
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
            self._mainGUI.author_folder = folder.text()
            self._mainGUI.user_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    self._mainGUI.response_flag = False
                    new_video_page(folder.text(), self._mainGUI)
                    break

        @QtCore.Slot()
        def _back_real_clicked(self):
            self._mainGUI.back_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    self._mainGUI.response_flag = False
                    server_response = self._mainGUI.server_response
                    if self._mainGUI.current_phase == "VIDEO_PAGE":
                        new_video_page(server_response["author"], self._mainGUI)
                        break
                    elif self._mainGUI.current_phase == "USERS":
                        new_user_page(self._mainGUI.current_page, self._mainGUI)
                        break
                    else:
                        print("idk man")
                        break
        
        @QtCore.Slot()
        def _home_clicked(self):
            self._mainGUI.current_page = 0
            self._mainGUI.home_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    self._mainGUI.response_flag = False
                    new_user_page(self._mainGUI.current_page, self._mainGUI)
                    self._mainGUI.response_flag = False
                    break

        @QtCore.Slot()
        def _upload_clicked(self):
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '.')
            self._mainGUI._upload_file_path = filename[0]
            self._mainGUI._upload_flag.set()

        @QtCore.Slot()
        def _forward_page_clicked(self):
            if self._mainGUI.current_page == self._max_page:
                return
            self._mainGUI.current_page += 1
            self._mainGUI.page_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_user_page(self._mainGUI.current_page, self._mainGUI)
                    self._mainGUI.response_flag = False
                    break

        @QtCore.Slot()
        def _back_page_clicked(self):
            if self._mainGUI.current_page == 0:
                return
            self._mainGUI.current_page -= 1
            self._mainGUI.page_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_user_page(self._mainGUI.current_page, self._mainGUI)
                    self._mainGUI.response_flag = False
                    break
        

    class Video_Page_GUI(QtWidgets.QWidget):

        def __init__(self, video_list, current_page, max_page, mainGUI, author):
            super().__init__()

            self._mainGUI = mainGUI
            self._video_list = video_list
            self._current_page = current_page
            self._max_page = max_page

            self._grid = QtWidgets.QGridLayout(self)
            row_value = 1
            column_value = 0
            for video in video_list:
                video_button = QtWidgets.QPushButton(f"{video['title']}", self)
                video_button.toolTip = video["id"]
                video_button.setFixedSize(100, 100)
                video_button.clicked.connect(self._folder_clicked)
                self._grid.addWidget(video_button, row_value, column_value, alignment=QtCore.Qt.AlignTop)
                if column_value == 4:
                    column_value = 0
                    row_value += 1
                else:
                    column_value += 1
            self._back = QtWidgets.QPushButton("<-", self)
            self._back.setFixedSize(50, 35)
            self._back.clicked.connect(self._back_page_clicked)
            self._forward = QtWidgets.QPushButton("->", self)
            self._forward.setFixedSize(50, 35)
            self._forward.clicked.connect(self._forward_page_clicked)
            self._title = QtWidgets.QLabel(f"{author}", alignment=QtCore.Qt.AlignTop)
            self._title.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
            self._home = QtWidgets.QPushButton("HOME", self)
            self._home.setFixedSize(50, 35)
            self._home.clicked.connect(self._home_clicked)
            self._back_real = QtWidgets.QPushButton("BACK", self)
            self._back_real.setFixedSize(50, 35)
            self._back_real.clicked.connect(self._back_real_clicked)
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
            id = folder.toolTip
            self._mainGUI.video_id = id
            self._mainGUI.video_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_video_player(self._mainGUI)
                    self._mainGUI.response_flag = False
                    break

        @QtCore.Slot()
        def _back_real_clicked(self):
            self._mainGUI.back_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    self._mainGUI.response_flag = False
                    server_response = self._mainGUI.server_response
                    if self._mainGUI.current_phase == "VIDEO_PAGE":
                        new_video_page(server_response["author"], self._mainGUI)
                        break
                    elif self._mainGUI.current_phase == "USERS":
                        new_user_page(self._mainGUI.current_page, self._mainGUI)
                        break
                    else:
                        print("idk man")
                        break

        @QtCore.Slot()
        def _home_clicked(self):
            self._mainGUI.current_page = 0
            self._mainGUI.home_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_user_page(self._mainGUI.current_page, self._mainGUI)
                    print("going home...")
                    self._mainGUI.response_flag = False
                    break

        @QtCore.Slot()
        def _upload_clicked(self):
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '.')
            self._mainGUI._upload_file_path = filename[0]
            self._mainGUI._upload_flag.set()

        @QtCore.Slot()
        def _forward_page_clicked(self):
            if self._mainGUI.current_page == self._max_page:
                return
            self._mainGUI.current_page += 1
            self._mainGUI.page_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_user_page(self._mainGUI.current_page, self._mainGUI)
                    self._mainGUI.response_flag = False
                    break

        @QtCore.Slot()
        def _back_page_clicked(self):
            if self._mainGUI.current_page == 0:
                return
            self._mainGUI.current_page -= 1
            self._mainGUI.page_flag.set()
            while True:
                if self._mainGUI.response_flag.is_set():
                    new_user_page(self._mainGUI.current_page, self._mainGUI)
                    self._mainGUI.response_flag = False
                    break
    
    class Video_Outside_GUI(QtWidgets.QWidget):
        
        def __init__(self, video_info, mainGUI):
            super().__init__()

            self._video_info = video_info

            self._layout = QtWidgets.QVBoxLayout(self)
            self._title = self._title = QtWidgets.QLabel(f"{self._video_info['author']}", alignment=QtCore.Qt.AlignTop)
            self._title.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
            self._video_player = self.VideoPlayer(mainGUI, self._video_info)
            #self._layout.addWidget(self._title)
            self._layout.addWidget(self._video_player)


        class VideoPlayer(QtWidgets.QWidget):
            def __init__(self, mainGUI, video_info):
                super().__init__()

                self._mainGUI = mainGUI
                self._video_info = video_info
                self._seg_num = 0
                self._last_segment_num = int(video_info["num_segments"]) - 1
                self._video_duration = int(video_info["length"])
                self._quality = video_info["max_quality"]
                self._mainGUI.segment_quality = self._quality
                self._mainGUI.segment_num = self._seg_num
                self._isPlaying = False
                self._segment_timer = None

                #slider
                self._seekSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
                self._seekSlider.setRange(0, self._video_duration)
                self._seekSlider.sliderReleased.connect(self._on_slider_released)

                # Media players, widgets, audio
                self._audio1 = QtMultimedia.QAudioOutput()
                self._audio2 = QtMultimedia.QAudioOutput()
                self._player1 = QtMultimedia.QMediaPlayer(self)
                self._player2 = QtMultimedia.QMediaPlayer(self)
                self._videoWidget1 = QtMultimediaWidgets.QVideoWidget()
                self._videoWidget2 = QtMultimediaWidgets.QVideoWidget()
                self._player1.setVideoOutput(self._videoWidget1)
                self._player1.setAudioOutput(self._audio1)
                self._player2.setVideoOutput(self._videoWidget2)
                self._player2.setAudioOutput(self._audio2)

                self._activePlayer = self._player1
                self._inactivePlayer = self._player2
                self._activeWidget = self._videoWidget1
                self._inactiveWidget = self._videoWidget2

                # Stack the two video widgets
                self._videoStack = QtWidgets.QStackedLayout()
                self._videoStack.addWidget(self._videoWidget1)
                self._videoStack.addWidget(self._videoWidget2)

                # Playback controls
                self._playButton = QtWidgets.QPushButton("Play")
                self._statusBar = QtWidgets.QLabel("Status: Idle")
                self._backButton = QtWidgets.QPushButton("Back")

                self._playButton.clicked.connect(self._toggle_play)
                self._backButton.clicked.connect(self._back_real_clicked)

                # Layouts
                controlLayout = QtWidgets.QHBoxLayout()
                controlLayout.addWidget(self._playButton)
                controlLayout.addWidget(self._backButton)

                mainLayout = QtWidgets.QVBoxLayout()
                mainLayout.addLayout(self._videoStack)
                mainLayout.addLayout(controlLayout)
                mainLayout.addWidget(self._seekSlider)
                mainLayout.addWidget(self._statusBar)
                self.setLayout(mainLayout)

                # Timer to manage segment end
                self._segmentTimer = QtCore.QTimer(self)
                self._segmentTimer.setInterval(100)
                self._segmentTimer.timeout.connect(self._check_segment_end)

                self._mainGUI.segment_request_flag.set()
                print("Built video player UI")

            def _toggle_play(self):
                if self._isPlaying:
                    self._activePlayer.pause()
                    self._segmentTimer.stop()
                    self._playButton.setText("Play")
                    self._update_status("Paused")
                    self._isPlaying = False
                else:
                    self._start_first_segment()
                    self._segmentTimer.start()
                    self._playButton.setText("Pause")
                    self._update_status("Playing")
                    self._isPlaying = True

            def _start_first_segment(self):
                self._activePlayer.setSource(QtCore.QUrl(str(self._mainGUI.next_segment)))
                self._activePlayer.play()
                self._videoStack.setCurrentWidget(self._activeWidget)
                self._segment_timer = time.time()
                print(f"Playing segment {self._seg_num}")
                self._seg_num += 1
                if self._seg_num <= self._last_segment_num:
                    self._mainGUI.segment_num = self._seg_num
                    self._mainGUI.segment_quality = self._quality
                    self._mainGUI.segment_request_flag.set()

            def _check_segment_end(self):
                if self._segment_timer is None:
                    return
                

                elapsed = time.time() - self._segment_timer
                is_last = self._seg_num - 1 == self._last_segment_num
                last_seg_length = self._video_duration % SEGMENT_DURATION or SEGMENT_DURATION
                duration = last_seg_length if is_last else SEGMENT_DURATION

                # Preload just before current segment ends
                if elapsed >= duration - 2 and self._mainGUI.segment_ready_flag.is_set():
                    self._inactivePlayer.setSource(QtCore.QUrl(str(self._mainGUI.next_segment)))
                    self._inactivePlayer.pause()
                    print(f"Preloaded segment {self._seg_num}")
                
                if self._segment_timer:
                    current_time = int((self._seg_num - 1) * SEGMENT_DURATION + (time.time() - self._segment_timer))
                    self._seekSlider.blockSignals(True)  # Prevent triggering user interaction handler
                    self._seekSlider.setValue(min(current_time, self._video_duration))
                    self._seekSlider.blockSignals(False)

                if elapsed >= duration:
                    if self._seg_num > self._last_segment_num:
                        self._activePlayer.stop()
                        self._segmentTimer.stop()
                        self._update_status("Playback finished")
                        self._playButton.setText("Play")
                        self._isPlaying = False
                        return

                    self._swap_players()

            def _swap_players(self):
                self._activePlayer.pause()
                self._inactivePlayer.play()
                self._videoStack.setCurrentWidget(self._inactiveWidget)

                # Swap references
                self._activePlayer, self._inactivePlayer = self._inactivePlayer, self._activePlayer
                self._activeWidget, self._inactiveWidget = self._inactiveWidget, self._activeWidget
                self._segment_timer = time.time()

                self._update_status(f"Playing Segment {self._seg_num}")
                print(f"Switched to segment {self._seg_num}")

                self._seg_num += 1
                if self._seg_num <= self._last_segment_num:
                    self._mainGUI.segment_num = self._seg_num
                    self._mainGUI.segment_quality = self._quality
                    self._mainGUI.segment_request_flag.set()

            def _back_real_clicked(self):
                self._mainGUI.back_flag.set()
                while True:
                    if self._mainGUI.response_flag.is_set():
                        self._mainGUI.response_flag.clear()
                        server_response = self._mainGUI.server_response
                        if self._mainGUI.current_phase == "VIDEO_PAGE":
                            new_video_page(server_response["result"][0]["author"], self._mainGUI)
                        elif self._mainGUI.current_phase == "USERS":
                            new_user_page(self._mainGUI.current_page, self._mainGUI)
                        else:
                            print("Unknown phase")
                        break

            def _update_status(self, message):
                self._statusBar.setText(f"Status: {message}")
            
            def _on_slider_released(self):
                desired_time = self._seekSlider.value()
                seg_num = desired_time // SEGMENT_DURATION
                offset_within_segment = desired_time % SEGMENT_DURATION

                if seg_num > self._last_segment_num:
                    seg_num = self._last_segment_num
                    offset_within_segment = 0

                self._seg_num = seg_num
                self._mainGUI.segment_num = seg_num
                self._mainGUI.segment_request_flag.set()

                def handle_jump():
                    if self._mainGUI.segment_ready_flag.is_set():
                        self._mainGUI.segment_ready_flag.clear()
                        self._inactivePlayer.setSource(QtCore.QUrl(str(self._mainGUI.next_segment)))
                        self._inactivePlayer.setPosition(offset_within_segment * 1000)  # ms
                        self._inactivePlayer.play()

                        self._activePlayer.pause()
                        self._videoStack.setCurrentWidget(self._inactiveWidget)
                        self._activePlayer, self._inactivePlayer = self._inactivePlayer, self._activePlayer
                        self._activeWidget, self._inactiveWidget = self._inactiveWidget, self._activeWidget
                        self._segment_timer = time.time() - offset_within_segment
                        self._update_status(f"Jumped to {desired_time}s")
                        print(f"Jumped to segment {seg_num}, offset {offset_within_segment}s")

                QtCore.QTimer.singleShot(100, handle_jump)  # Give system a moment to fetch


def new_user_page(page_num, mainGUI):
    sr = mainGUI.server_response
    mainGUI.create_user_page(sr["result"], sr["current_page"], sr["max_page"])
    mainGUI.current_page = page_num

def new_video_page(author, mainGUI):
    sr = mainGUI.server_response
    print("Server response recieved!")
    mainGUI.create_video_page(sr["result"], sr["current_page"], sr["max_page"], author)
    mainGUI.current_page = sr["current_page"]

def new_video_player(mainGUI):
    mainGUI.create_video_player()

def run_gui():
    app = QtWidgets.QApplication([])

    button = GUI()
    button.resize(800, 600)
    button.show()

    sys.exit(app.exec())
