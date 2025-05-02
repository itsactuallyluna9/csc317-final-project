import socket
import threading
import json
import os
from pathlib import Path
from typing import Tuple

HOST = "0.0.0.0"
PORT = 2121
SEGMENT_SIZE = 1024

class ClientState:  # we may not need this anymore i dont think - trey, we aren't really moving through folders anymore
    """
    Holds state for each client, created so multiple clients can have their own current working directory
    """

    def __init__(self, conn: socket.socket, addr: Tuple[str, int]):
        self.conn = conn
        self.addr = addr
        #self.cwd = os.getcwd() 
        self.__server_root = Path.cwd()

    def safety_check(self, path: Path) -> bool:
        """
        Check if the path is valid.

        For a path to be valid, it must be under the server's root directory.
        """

        # this needs to work on python 3.8, we can't use is_relative_to() because it was added in 3.9 :<
        try:
            # convert to absolute path, resolve symlinks
            abs_path = Path(path).resolve()
            # is the server root in the path?
            return (
                self.__server_root in abs_path.parents or abs_path == self.__server_root
            )
        except (ValueError, OSError):
            # handle any path-related errors
            return False

def main():
    """
    Start the FTP server and handle incoming connections.
    """

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((HOST, PORT))
            server.listen()
            print(f"[Server is listening on HOST = {HOST}, PORT = {PORT}]")
            while True:
                conn, addr = server.accept()
                client = ClientState(conn, addr)
                thread = threading.Thread(
                    target=handle_client, args=(client,), daemon=True
                )
                thread.start()
    finally:
        print("[Server shutting down]")
        server.close()


def handle_client(client: ClientState) -> None:
    """
    Handle a client connection.
    """

    print("[New Connection]")
    while True:
        packet = client.conn.recv(SEGMENT_SIZE).decode("utf-8")
        if not packet:
            break
        packet = json.loads(packet)

        """ may still need
        if packet.get("target") is not None:
            # we have a target to check!
            target_path = Path(packet["target"])
            if not client.safety_check(target_path):  # check if the path is valid
                client.conn.send(
                    f"Invalid path (via safety check): {target_path}".encode("utf-8")
                )
                continue
            """
        # handling to upload, modify videos
        if packet["type"] == "UPLOAD":
            file_name = packet["target"]
            upload(client.conn, file_name, packet["file_size"])
            client.conn.send(b"Upload Finished")

        elif packet["type"] == "DOWNLOAD":
            # send a file from the server to the client
            file_name = Path(client.cwd) / packet["target"]
            download(client.conn, file_name)

        #elif packet["type"] == "LIST":
        #    client.conn.send(listdir(client.cwd).encode("utf-8"))

        elif packet["type"] == "DELETE":
            file_name = packet["target"]
            delete(client, file_name)
            # client.conn.send(b"File Deleted") # commented for now, see if we cant solve that weird issue ~luna

        # data handling for clients gui and actions below
        elif packet["type"] == "LOGIN":
            pass

        elif packet["type"] == "REGISTER":
            pass

        elif packet["type"] == "USERS":
            pass

        elif packet["type"] == "VIDEO_PAGE":
            pass

        elif packet["type"] == "VIDEOS":
            pass

        else:
            client.conn.send(b"[Command Not Found]")

    client.conn.close()


def upload(conn: socket.socket, file_name: str, file_size: int) -> None:
    """
    Handle file upload from client.
    """

    conn.send(b"ACK")
    completed = 0
    with open(file_name, "wb") as f:
        while completed < file_size:
            data = conn.recv(SEGMENT_SIZE)
            f.write(data)
            completed += len(data)
    print(
        f"File with name {file_name} by the user {conn.getpeername()[0]} uploaded to the server."
    )


def download(conn: socket.socket, file_name: str) -> None:
    """
    Handle file download to client.
    """

    # personally, i love the pathlib api
    # so im using it because there's enough to worry about already
    file_path = Path(file_name)
    if not file_path.is_file():  # also checks if it exists
        # we can't send!!!
        conn.send(f"File not found at target path {file_name}".encode("utf-8"))
        return

    # we can send! first lets get the file size
    file_size = file_path.stat().st_size
    # and we're gonna be sending the file :>
    # since the client's a bit weird, we'll be sending a json object
    # (which the client will hopefully pick up on)
    # and then the file itself once the client's ready.
    send_obj(
        conn,
        {
            "type": "DOWNLOAD",
            "target": file_path.name,
            "file_size": file_size,
        },
    )

    ack = conn.recv(SEGMENT_SIZE)  # check for ACK from client
    if ack != b"ACK":
        print("Client did not acknowledge file metadata! Aborting transfer.")
        return

    # now we can send the file
    with open(file_name, "rb") as file:
        while True:
            data = file.read(SEGMENT_SIZE)
            if not data:
                break
            conn.sendall(data)

    # and we're done, the client will know when we're done (because of the file_size we sent earlier)
    print(
        f"File {file_name} sent to client @ {conn.getpeername()[0]}"
    )  # this is the ip of the client, not the server


def delete(client: ClientState, file_name: str) -> None:
    """
    Handle file deletion request from client.
    """

    target_path = os.path.abspath(
        os.path.join(client.cwd, file_name)
    )  # this is whats gonna be deleted, if you were in /Users/trey and file_name is 'bob.txt' it would delete /Users/trey/bob.txt

    try:
        os.remove(target_path)
        print(f"File {target_path} removed from server by Client @ {client.addr[0]}")
        client.conn.send(f"Deleting file at {target_path}".encode("utf-8"))
    except FileNotFoundError:
        client.conn.send("File not found! Check path".encode("utf-8"))
    except OSError:  # if the path is a directory we have to use rmdir()
        os.rmdir(target_path)
        print(
            f"Directory {target_path} removed from server by Client @ {client.addr[0]}"
        )
        client.conn.send(f"Deleting directory at {target_path}".encode("utf-8"))


def send_obj(conn: socket.socket, obj: dict) -> None:
    """
    Sends a JSON object to the client.
    """

    json_obj = json.dumps(obj)
    conn.sendall(json_obj.encode("utf-8"))


if __name__ == "__main__":
    main()
