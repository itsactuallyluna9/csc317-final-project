import socket
import json
import re
import threading
import os
from typing import Optional, Dict, Union
from pathlib import Path
from wonderful_gui import GUI, run_gui

#def interpret_command(command_str: str) -> Optional[Dict[str, Union[str, int]]]:
#    """
#    Formats the client command into a JSON dictionary to send to server.
#    """
#
#    stripped_command = command_str.strip()
#    no_quote_command = stripped_command.replace("'", "")
#
#    commands_without_path = ["LIST", "EXIT", "CLIST", "HELP"]
#    commands_with_path = ["DOWNLOAD", "DELETE", "UPLOAD", "CCWD"]
#    commands_with_optional_path = ["CWD"]
#    path = " ('[-\w.\s]+'|[-\w.]+)(/('[-\w.\s]+'|[-\w.]+))*/?" #regex expression for file path
#    optional_path = f"({path})?"
#
#    no_path = ["^" + command + "$" for command in commands_without_path]
#    with_path = ["^" + command + path + "$" for command in commands_with_path]
#    with_optional_path = [
#        "^" + command + optional_path + "$" for command in commands_with_optional_path
#    ]
#
#    commands = no_path + with_path + with_optional_path
#    regex_pattern = f"{'|'.join(commands)}"
#
#    if not re.search(regex_pattern, stripped_command): #check if client command is valid
#        print("Invalid command")
#        return None
#
#    if " " in no_quote_command:
#        command_type, arg = no_quote_command.split(" ", maxsplit=1)
#    else:
#        command_type = stripped_command
#        arg = None
#
#    request_dict = {}
#
#    request_dict["type"] = command_type
#
#    if arg is not None:
#        request_dict["target"] = arg
#
#    return request_dict


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


def send_command(
    client_socket: socket.socket, request_dict: Dict[str, Union[str, int]]
) -> None:
    """
    sends parsed command to server
    """

    if request_dict["type"] == "UPLOAD":
        byte_file = get_upload_file(request_dict)
        if byte_file is None:
            return

    command_to_send = json.dumps(request_dict).encode("utf-8")
    client_socket.sendall(command_to_send)

    if request_dict["type"] == "UPLOAD":
        client_socket.recv(1024).decode("utf-8")
        client_socket.sendall(byte_file)


def receive_reply(client_socket: socket.socket, command_type: str) -> None:
    """
    Recieves reply from server. If the command type is DOWNLOAD, sends the
    request dictionary and recieves the file. Otherwise, recieve and print
    message from server.
    """

    if command_type == "DOWNLOAD":
        # call the download function
        # yippie we're downloading!!
        # server's gonna send us some metadata: namely size and name
        metadata = json.loads(client_socket.recv(1024).decode("utf-8"))
        if metadata.get("type") != "DOWNLOAD":
            raise Exception("Server did not send download metadata!")

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
    else:
        reply = client_socket.recv(1024).decode("utf-8")
        print(reply)


def run_client(gui: GUI) -> None:
    """
    connect and handle client connection to FTP server
    """

    server_ip = "luna"  # placeholder
    server_port = 2121  # placeholder
    input_loop = True  # keep asking client for new command

    print("Welcome! HELP for command list.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, server_port))

        while True: # login loop
            if gui.login_flag.is_set():
                login_data = get_user_credentials()
                if login_data: #continues if valid attempt
                    login_data["type"] = "LOGIN"
                    server_response = request_server(client_socket, login_data)
                gui.login_flag = False

            if gui.registration_flag.is_set():
                regis_data = get_user_credentials()
                if regis_data: #continues if valid attempt
                    regis_data["type"] = "REGISTER"
                    server_response = request_server(client_socket, regis_data)
                gui.registration_flag = False

            if server_response["type"] == "ERROR": #error message form server not dictionary; need to fix
                #display error on gui
                pass
            
            else:
                gui.server_response = server_response
                #move login loop to its own function to allow for logout?
                break
        in_videos_page = False
        author = ""
        previous_pages = []
        while True: #navigation loop
            if gui.page_flag.is_set():
                page_request = get_page_num(gui)
                if in_videos_page:
                    page_request["type"] = "VIDEO_PAGE"
                    page_request["author_name"] = author
                else:
                    page_request["type"] = "USERS"
                page = request_server(client_socket, page_request)
                #check errors
                gui.server_response = page
                gui.page_flag = False

            if gui.user_flag.is_set():
                in_videos_page = True
                #author = get author from gui
                #previous_pages.append(page_num  from gui)
                author_request = {}
                author_request["type"] = "VIDEO_PAGE"
                author_request["author"] = author
                author_request["page_num"] = 1
                author_page = request_server(client_socket, author_request)
                #check errors
                gui.server_response = author_page
                gui.user_flag = False
            
            if gui.home_flag.is_set():
                previous_pages = []
                home_request = {}
                home_request["type"] = "USERS"
                home_request["page_num"] = 1 # assuming page_num is in integers right now
                home_page = request_server(client_socket, home_request) #use page instead?
                #check errors
                gui.server_response = home_page
                gui.home_flag = False
            
            if gui.back_flag.is_set():
                last_page_num = previous_pages.pop()
                last_page_request = {}
                if not previous_pages:
                    last_page_request["type"] = "USERS"
                else:
                    last_page_request["type"] = "VIDEO_PAGE"
                    last_page_request["author"] = author
                    in_videos_page = True

                last_page_request["page_num"] = last_page_num
                last_page = request_server(client_socket, last_page_request)
                #check errors
                gui.server_response = last_page
                gui.back_flag = False

            if gui.video_flag.is_set():
                in_videos_page = False
                video_request = {}
                video_request["type"] ="VIDEOS"
                #video_request["video_id"] = get video_id from gui
                #segment_num???
                #quality???
                #maybe get response from server and request segment_num and quality afterward

                gui.video_flag = False

                


        #while input_loop:
        #    client_command = input(">")
        #    request_dict = interpret_command(client_command)
#
        #    if request_dict is not None:
        #        if request_dict["type"] == "CCWD":
        #            if "target" not in request_dict:
        #                print(os.getcwd())
        #            try:
        #                os.chdir(request_dict["target"])
        #                print(
        #                    f"Client Working Directory changed to {request_dict['target']}."
        #                )
        #            except OSError:
        #                print(f"{request_dict['target']} is not a valid path")
        #        elif request_dict["type"] == "EXIT":
        #            input_loop = False
#
        #        elif request_dict["type"] == "CLIST":
        #            dir_items = os.listdir(os.getcwd())
#
        #            for item in dir_items:
        #                print(item)
        #        elif request_dict["type"] == "HELP":
        #            print("LIST\nUPLOAD\nDOWNLOAD\nDELETE\nCWD\nCCWD\nCLIST\nEXIT")
#
        #        else:
        #            send_command(client_socket, request_dict)
        #            receive_reply(client_socket, request_dict["type"])


def get_user_credentials(gui: GUI) -> Dict:
    """
    Gets and checks username and password from gui
    """
    user_cred = {}
    user_cred['username'] = gui.username
    user_cred['password'] = gui.password
    empty_box = any(value == "" for value in user_cred.values()) #checks if username or password were not filled
    if empty_box:
        return {} #invalid attempt
    return user_cred


def get_page_num(gui: GUI) -> Dict:
    """
    Gets requested page number from gui
    """
    page_num = {}
    #page_num["page_num"] = gui.
    return page_num


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
    gui = GUI()
    gui.run_gui()
    network_thread = threading.Thread(target = run_client)
    network_thread.start()    
