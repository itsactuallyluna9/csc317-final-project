import socket
import json
import threading
import time
from tempfile import TemporaryDirectory
from typing import Optional, Dict, Union
from pathlib import Path
from wonderful_gui import GUI
from PySide6 import QtWidgets
from queue import Queue

def run_client(gui: GUI) -> None:
    """
    connect and handle client connection to FTP server
    """
    server_ip = "luna"
    server_port = 2121

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, server_port))

        while True:
            login(client_socket, gui)
            navigate(client_socket, gui)


def login(client_socket: socket.socket, gui: GUI) -> None:
    """
    Checks and handles login flags from gui
    """
    while True: # login loop
            if gui.login_flag.is_set():
                gui.login_flag = False
                login_finished = handle_login_attempt(client_socket, gui, "LOGIN")

                if login_finished:
                    break

            if gui.registration_flag.is_set():
                gui.registration_flag = False
                register_finished = handle_login_attempt(client_socket, gui, "REGISTER")

                if register_finished:
                    break


def navigate(client_socket: socket.socket, gui: GUI) -> None:
    """
    Check and handles navigation flags from gui
    Also allows start of downloading and viewing videos
    """
    in_videos_page = False
    author = ""
    previous_pages = [] #holds page number of previous pages
    current_segment = Queue()
    stop_signal = threading.Event()
    thread_running = threading.Event()
    thread_lock = threading.Lock()

    while True:
        if gui.page_flag.is_set():
            gui.page_flag = False
            page_request = {}
            page_request["page_num"] = gui.current_page

            if in_videos_page:
                page_request["type"] = "VIDEO_PAGE"
                page_request["author_name"] = author
            else:
                page_request["type"] = "USERS"

            page = request_server(client_socket, page_request)
            #check errors
            send_to_gui(page, gui)

        if gui.user_flag.is_set():
            gui.user_flag = False
            in_videos_page = True
            author = gui.author_folder
            previous_pages.append(gui.current_page)
            author_request = {}
            author_request["type"] = "VIDEO_PAGE"
            author_request["author"] = author
            author_request["page_num"] = 0
            author_page = request_server(client_socket, author_request)
            #check errors
            send_to_gui(author_page, gui)
        
        if gui.home_flag.is_set():
            gui.home_flag = False
            previous_pages = []
            home_request = {}
            home_request["type"] = "USERS"
            home_request["page_num"] = 0
            home_page = request_server(client_socket, home_request)
            #check errors
            send_to_gui(home_page, gui)
        
        if gui.back_flag.is_set():
            gui.back_flag = False
            last_page_num = previous_pages.pop()
            last_page_request = {}

            if not previous_pages:
                last_page_request["type"] = "USERS"
                gui.current_phase = "USERS"
            else:
                last_page_request["type"] = "VIDEO_PAGE"
                last_page_request["author"] = author
                gui.current_phase = "VIDEO_PAGE"
                in_videos_page = True

            last_page_request["page_num"] = last_page_num
            last_page = request_server(client_socket, last_page_request)
            #check errors
            send_to_gui(last_page, gui)

        if gui.video_flag.is_set():
            gui.video_flag = False
            in_videos_page = False
            previous_pages.append(gui.current_page)

            video_info_request = {}
            video_id = gui.video_id
            video_info_request["type"] ="VIDEO_INFO"
            video_info_request["video_id"] = video_id

            video_info = request_server(client_socket, video_info_request)
            send_to_gui(video_info, gui)

            starting_quality = video_info["max_quality"]
            num_segment = video_info["num_segments"]

            with TemporaryDirectory() as segment_dir:
                download_video_thread = threading.Thread(target=request_video,
                                                         args=(client_socket,
                                                               segment_dir,
                                                               video_id,
                                                               0,
                                                               starting_quality,
                                                               num_segment,
                                                               current_segment,
                                                               stop_signal,
                                                               thread_running,
                                                               thread_lock))

                back_to_navigation = wait_for_thread_end(gui, thread_running)

                if not back_to_navigation:
                    thread_running.set()
                    download_video_thread.start()
                    run_video(client_socket, gui, segment_dir, video_id, current_segment, stop_signal, thread_running, thread_lock)

        if gui.upload_flag.is_set():
            gui.upload_flag = False
            upload_video(client_socket, gui.upload_file_path)

        #if gui.logout_flag.is_set():
            #gui.logout_flag = False
            #break #return to login
        
    
def run_video(client_socket: socket.socket, gui: GUI, segment_dir: TemporaryDirectory, video_id: int, current_segment: Queue, stop_signal: threading.Event, thread_running: threading.Event, thread_lock: threading.Lock) -> None:
    """
    Gives video segments to gui and responds to video flags in gui
    """
    while True:
        if gui.segment_request_flag.is_set():
            gui.segment_request_flag = False
            next_segment = gui.segment_num
            quality = gui.segment_quality
            get_segment(client_socket, gui, segment_dir, video_id, quality, next_segment, current_segment, stop_signal, thread_running, thread_lock)
        
        if check_back_to_navigation(gui):
            if thread_running.is_set():
                with thread_lock:
                    stop_signal.set() #stop download_video_thread

            break #returns to navigation to handle flag


def get_segment(client_socket: socket.socket, gui: GUI, segment_dir: TemporaryDirectory, video_id: int, quality: int, segment_num: int, current_segment: Queue, stop_signal: threading.Event, thread_running: threading.Event, thread_lock: threading.Lock) -> None:
    """
    gets video segment and gives it to gui
    """
    video = f"{video_id}_{quality}_{segment_num}.mp4"
    video_path = Path(segment_dir).joinpath(video)

    while True:
        if video_path.exists():
            gui.next_segment = video_path
            break #go back to checking flags in run_video

        else:
            if thread_running.is_set():
                downloading_segment = ""
                with thread_lock:
                    if current_segment.qsize > 0:
                        downloading_segment = current_segment.get()
                        current_segment.put(downloading_segment)
                    else:
                        continue #wait to see what is being downloaded

                if downloading_segment == video: #checks if video is being downloaded currently
                    continue

                with thread_lock:
                    stop_signal.set() #stops current download thread if it is downloading different segment than requested segment
    
            download_video_thread = threading.Thread(target=request_video,
                                                     args=(client_socket,
                                                           segment_dir,
                                                           video_id,
                                                           segment_num,
                                                           quality,
                                                           segment_num,
                                                           current_segment,
                                                           stop_signal,
                                                           thread_running,
                                                           thread_lock),
                                                           daemon = True)
            
            back_to_navigation = wait_for_thread_end(gui, thread_running)

            if back_to_navigation: #check whether to continue download attempt
                break

            thread_running.set()
            download_video_thread.start()


def request_video(client_socket: socket.socket, segment_dir: TemporaryDirectory, video_id: int, starting_segment: int, quality: int, num_segment: int, current_segment: Queue, stop_signal: threading.Event, thread_running: threading.Event, thread_lock: threading.Lock) -> None:
    """
    Requests video segments
    """
    next_segment = starting_segment
    last_segment = num_segment - 1
    next_segment_request = {}
    next_segment_request["type"] = "VIDEO"
    next_segment_request["video_id"] = video_id

    while next_segment <= last_segment and not stop_signal.is_set():
        segment_name = f"{video_id}_{quality}_{next_segment}.mp4"
        extended_segment_name = Path(segment_dir).joinpath(segment_name)

        if Path(extended_segment_name).exists():
            break #stop segment download if the segment has already been downloaded

        with thread_lock:
            current_segment.put(segment_name) #stores current segment being downloaded for checking in network_thread

        next_segment_request["segment_id"] = next_segment
        next_segment_request["quality"] = quality
        video_metadata = request_server(client_socket, next_segment_request)
        receive_reply(client_socket, video_metadata, segment_dir)
        next_segment += 1

        with thread_lock:
            current_segment.get() #remove stored segement_name

    with thread_lock:
        stop_signal.clear() #allows reuse of stop_signal
        thread_running.clear()


def check_back_to_navigation(gui: GUI) -> bool:
    """
    Returns True when a gui flag that needs to handled in navigation is set
    """
    go_to_navigation = gui.back_flag.is_set() or gui.home_flag.is_set() #or gui.logout_flag.is_set()
    return go_to_navigation


def wait_for_thread_end(gui: GUI, thread_running: threading.Event) -> bool:
    """
    Waits for download thread to finish stopping
    """
    while thread_running.is_set():
        time.sleep(0.1)

        if check_back_to_navigation(gui):
            return True
        
    return False


def send_to_gui(server_response: Dict, gui: GUI) -> None:
    """
    Informs gui of server response
    """
    gui.server_response = server_response
    gui.response_flag = True


def handle_login_attempt(client_socket: socket.socket, gui: GUI, type: str) -> bool:
    """
    gives login info to server and signals gui with server response
    """
    login_data = get_user_credentials(gui)

    if login_data: #continues if valid attempt
        login_data["type"] = type
        server_response = request_server(client_socket, login_data)

        if server_response["type"] == "ERROR":
            gui.login_failure = True
            return False
        
        gui.server_response = server_response
        gui.login_success = True
        return True
    
    return False


def get_user_credentials(gui: GUI) -> Dict:
    """
    Gets and checks username and password from gui
    """
    user_cred = {}
    user_cred['username'] = gui.login_page.username
    user_cred['password'] = gui.login_page.password
    empty_box = any(value == "" for value in user_cred.values()) #checks if username or password were not filled

    if empty_box:
        return {} #invalid attempt
    
    return user_cred


def get_upload_file(request_dict: Dict[str, Union[str, int]]) -> Optional[bytes]:
    """
    Update the request dictionary for upload protocol and loads the file.
    """
    try:
        with open(request_dict["target"], "rb") as upload_file:
            byte_file = upload_file.read()

        request_dict["file_size"] = Path(request_dict["target"]).stat().st_size
    except FileNotFoundError:
        print(f"File: {request_dict['target']} not found.")
        return None
    
    return byte_file


def upload_video(
    client_socket: socket.socket, path: str
) -> None:
    """
    Uploads video to server
    """
    request_dict = {}
    request_dict["type"] = "UPLOAD"
    request_dict["target"] = path
    request_dict["title"] = "You have no choice. Deal with it."
    byte_file = get_upload_file(request_dict)

    request_server(client_socket, request_dict)
    client_socket.sendall(byte_file)


def receive_reply(client_socket: socket.socket, metadata: Dict, segment_dir: TemporaryDirectory) -> None:
    """
    Recieves reply from server. If the command type is DOWNLOAD, sends the
    request dictionary and recieves the file. Otherwise, recieve and print
    message from server.
    """
    file_name = metadata.get("target")
    extended_file_name = Path(segment_dir).joinpath(file_name)
    file_size = metadata.get("file_size")
    print(f"Downloading {extended_file_name} of size {file_size} bytes")
    client_socket.sendall(b"ACK")  # acknowledge the metadata
    # let's do it
    bytes_received = 0

    with open(extended_file_name, "wb") as file:
        while bytes_received < file_size:
            data = client_socket.recv(1024)

            if not data:
                break

            file.write(data)
            bytes_received += len(data)

    print(f"Downloaded {extended_file_name} of size {bytes_received} bytes")


def delete_video(client_socket: socket.socket, video_id: int) -> None:
    """
    Deletes the video from the server and prints the response from the server. 
    """
    request_dict = {}
    request_dict['type'] = 'DELETE'
    request_dict['video_id'] = video_id
    response = request_server(client_socket, request_dict)

    if response['success']:
        print('The video has been successfully deleted')
    else:
        print('Video Deletion is unsuccessful. Please make sure the video_id is correct and try again.')
                

def request_server(client_socket: socket.socket, request_dict: Dict) -> Dict:
    """
    Sends request dictionary to server and recieves server response
    """
    request_json = json.dumps(request_dict)
    client_socket.sendall(request_json.encode("utf-8"))
    response_json = client_socket.recv(1024).decode("utf-8") #error message not dictionary; need to fix
    response = json.loads(response_json)
    return response
    

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    button = GUI()
    network_thread = threading.Thread(target = run_client, args=(button, ))
    network_thread.start()
    button.resize(800, 600)
    button.show()

    exit(app.exec())
