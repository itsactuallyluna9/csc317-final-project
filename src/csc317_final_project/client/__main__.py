import socket
import json
import threading
import time
from typing import Optional, Dict, Union
from pathlib import Path
from wonderful_gui import GUI
from PySide6 import QtWidgets

def run_client(gui: GUI) -> None:
    """
    connect and handle client connection to FTP server
    """

    server_ip = "luna"  # placeholder
    server_port = 2121  # placeholder

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, server_port))
        login(client_socket, gui)
        navigate(client_socket, gui)


def login(client_socket: socket.socket, gui: GUI) -> None:
    """
    Checks and handles login flags from gui
    """
    while True: # login loop
            if gui.login_flag.is_set():
                gui.login_flag = False
                login_data = get_user_credentials(gui)
                if login_data: #continues if valid attempt
                    login_data["type"] = "LOGIN"
                    server_response = request_server(client_socket, login_data)
                    if server_response["type"] == "ERROR": #error message form server not dictionary; need to fix
                        gui.login_failure = True
                    else:
                        gui.server_response = server_response
                        gui.login_success = True
                        #move login loop to its own function to allow for logout?
                        break

            if gui.registration_flag.is_set():
                gui.registration_flag = False
                regis_data = get_user_credentials(gui)
                if regis_data: #continues if valid attempt
                    regis_data["type"] = "REGISTER"
                    server_response = request_server(client_socket, regis_data)
                    
                    if server_response["type"] == "ERROR": #error message form server not dictionary; need to fix
                        gui.login_failure = True
                    else:
                        gui.server_response = server_response
                        gui.login_success = True
                        #move login loop to its own function to allow for logout?
                        break


def navigate(client_socket: socket.socket, gui: GUI) -> None:
    """
    Check and handles navigation flags from gui
    Also allows start of downloading and viewing videos
    """
    in_videos_page = False
    author = ""
    previous_pages = [] #holds page number of 
    stop_signal = threading.Event()
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
            video_info_request = {}
            video_info_request["type"] ="VIDEO_INFO"
            #video_request["video_id"] = get video_id from gui
            video_info = request_server(client_socket, gui)
            download_video_thread = threading.Thread(target=request_video,
                                                     args=(client_socket,
                                                           gui,
                                                           0,
                                                           video_info["max_quality"],
                                                           video_info["num_segment"],
                                                           stop_signal))
            download_video_thread.start()

        if gui.upload_flag.is_set():
            gui.upload_flag = False
            upload_video(client_socket, gui.upload_file_path)


def request_video(client_socket: socket.socket, gui: GUI, starting_segment: int, quality: int, num_segment: int, stop_signal: threading.Event) -> None:
    """
    Requests video segments
    """

    next_segment = starting_segment
    next_segment_request = {}
    next_segment_request["type"] = "VIDEO"

    while next_segment <= (num_segment - 1) and not stop_signal.is_set():
        next_segment_request["segment_num"] = next_segment
        next_segment_request["quality"] = quality
        video_metadata = request_server(client_socket, next_segment_request)
        receive_reply(client_socket, video_metadata)
        next_segment += 1

    stop_signal.clear() #allows reuse of stop_signal
    return
        
    
def run_video(client_socket: socket.socket, gui: GUI, num_segment: int, stop_signal: threading.Event):
    """
    Gives video segments to gui and responds to video flags in gui
    """
    #give first video
    while True:
        pass
        #if gui.(next_segment_flag).is_set():
            #gui.(next_segment_flag) = False

        #if gui.( flag for changing video time).is_set():
            #gui.( flag for changing video time) = False
            #

        #if gui.( change video quality).is_set():
            #gui.( change video quality) = False
            #stop_signal.set()
            #segment_num = gui.(current_segement_number)
            #new_quality = gui.(quality)
            #download_video_thread = threading.Thread(target=request_video,
            #                                         args=(client_socket,
            #                                               gui,
            #                                               segment_num,
            #                                               new_quality,
            #                                               num_segment,
            #                                               stop_signal),
            #                                               daemon = True)
            #while stop_signal.is_set():
                #time.sleep(0.1)
            #download_video_thread.start()
            #get_segment(quality, segment_num)
            #give first segment to gui


def get_segment(video_id: int, quality: int, segment_num: int) -> None:
    """
    gets video segment and gives it to gui
    """
    #video = 
    pass


def send_to_gui(server_response: Dict, gui: GUI) -> None:
    """
    Informs gui of server response
    """
    gui.server_response = server_response
    gui.response_flag = True


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


def receive_reply(client_socket: socket.socket, metadata: Dict) -> None:
    """
    Recieves reply from server. If the command type is DOWNLOAD, sends the
    request dictionary and recieves the file. Otherwise, recieve and print
    message from server.
    """
    
    file_name = metadata.get("target")
    file_size = metadata.get("file_size")
    print(f"Downloading {file_name} of size {file_size} bytes")
    client_socket.sendall(b"ACK")  # acknowledge the metadata
    # let's do it
    bytes_received = 0
    with open(file_name, "wb") as file:
        while bytes_received < file_size:
            data = client_socket.recv(1024)
            if not data:
                break
            file.write(data)
            bytes_received += len(data)
    print(f"Downloaded {file_name} of size {bytes_received} bytes")
                

def request_server(client_socket: socket.socket, request_dict: Dict) -> Dict:
    """
    Sends request dictionary to server and recieves server response
    """
    request_json = json.dumps(request_dict)
    client_socket.sendall(request_json.encode("utf-8"))
    response_json = client_socket.recv(1024).decode("utf-8") #error message not dictionary; need to fix
    response = json.loads(response_json)
    return response


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


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    button = GUI()
    network_thread = threading.Thread(target = run_client, args=(button, ))
    network_thread.start()
    button.resize(800, 600)
    button.show()

    exit(app.exec())
       
