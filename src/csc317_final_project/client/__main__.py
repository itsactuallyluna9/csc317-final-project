import socket
import json
import re
import threading
import os
from typing import Optional, Dict, Union
from pathlib import Path
from wonderful_gui import GUI

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

        while True:
            if gui.login_flag.is_set():
                login_data = get_login_data()
                server_response = check_login(login_data)
            if gui.registration_flag.is_set():
                regis_data = get_registration_data()
                server_response = check_login(regis_data)

            #give data to gui
                


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


def get_login_data(gui: GUI):
    """
    Gets username and password from gui
    """
    login_dict = {}
    login_dict['username'] = gui.username #get username from gui
    login_dict['password'] = gui.password #get password from gui
    login_dict['type'] = 'login'
    return login_dict

def get_registration_data(gui: GUI):
    """
    Gets username and password to register a new user.
    """
    regis_dict = {}
    regis_dict['username'] = gui.username
    regis_dict['password'] = gui.password
    regis_dict['type'] = 'register'
    return regis_dict


def check_login(client_socket: socket.socket, login_data: Dict) -> Dict:
    client_socket.sendall(login_data)
    response = client_socket.recv(1024)
    return response
    

if __name__ == "__main__":
    gui = GUI()
    gui.run_gui()
    network_thread = threading.Thread(target = run_client)
    network_thread.start()    
