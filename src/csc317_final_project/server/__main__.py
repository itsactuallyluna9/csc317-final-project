import socket
import threading
import json
from pathlib import Path
from typing import Optional

from csc317_final_project.server.db import Database

SEGMENT_SIZE = 1024


class Server:
    def __init__(
        self, server_path: Path, host: str = "0.0.0.0", port: int = 2121
    ) -> None:
        self.host = host
        self.port = port
        self.db = Database(server_path)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))

    def start(self) -> None:
        """
        Start the server and listen for incoming connections.

        This method will run indefinitely, accepting new connections and spawning a new thread for each client.
        """
        self.server.listen()
        print(f"[Server is listening on HOST = {self.host}, PORT = {self.port}]")
        try:
            while True:
                conn, addr = self.server.accept()
                print(f"[New Connection] {addr}")
                thread = threading.Thread(target=self.handle_client, args=(conn,))
                thread.start()
        except KeyboardInterrupt:
            print("[Server shutting down]")
        finally:
            self.server.close()
            print("[Server closed]")

    def handle_client(self, client: socket.socket) -> None:
        """
        Handle a client connection.
        """

        print("[New Connection]")
        while True:
            packet = client.recv(SEGMENT_SIZE).decode("utf-8")
            if not packet:
                break
            recieved_obj = json.loads(packet)
            print(f"[Recieved] {recieved_obj}")
            try:
                to_client = self.handle_command(client, recieved_obj)
                if to_client:
                    send_obj(client, to_client)
            except Exception as e:
                send_obj(
                    client,
                    {
                        "type": "ERROR",
                        "message": str(e),
                    },
                )

        client.close()

    def handle_command(
        self, client: socket.socket, recieved_obj: dict
    ) -> Optional[dict]:
        # handling to upload, modify videos
        if recieved_obj["type"] == "UPLOAD":
            file_name = recieved_obj["target"]
            upload(client, file_name, recieved_obj["file_size"])

        elif recieved_obj["type"] == "DOWNLOAD":
            # send a file from the server to the client
            file_name = Path.cwd / recieved_obj["target"]
            download(client, file_name)

        # data handling for clients gui and actions below
        elif recieved_obj["type"] == "LOGIN":
            success = self.db.login(
                recieved_obj["username"],
                recieved_obj["password"],
            )
            if success:
                # they want the first page of users on successful login
                # so...
                self.handle_command(
                    client,
                    {
                        "type": "USERS",
                        "page_num": 0,
                    },
                )
            else:
                raise Exception("Login failed")

        elif recieved_obj["type"] == "REGISTER":
            success = self.db.register(
                recieved_obj["username"],
                recieved_obj["password"],
            )
            if success:
                # they want the first page of users on successful login/register
                # so...
                self.handle_command(
                    client,
                    {
                        "type": "USERS",
                        "page_num": 0,
                    },
                )
            else:
                raise Exception("Registration failed")

        elif recieved_obj["type"] == "USERS":
            # get the users from the database
            page_num = recieved_obj["page_num"]
            users = self.db.get_users_page(page_num)
            send_obj(client, users)

        elif recieved_obj["type"] == "VIDEO_PAGE":
            raise NotImplementedError("what")

        elif recieved_obj["type"] == "VIDEOS":
            # get the videos from the database
            page_num = recieved_obj["page_num"]
            author = recieved_obj.get("author", None)
            videos = self.db.get_video_page(page_num, author)
            send_obj(client, videos)

        else:
            raise NotImplementedError(
                f"Command {recieved_obj['type']} not implemented yet!! :<"
            )


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


def send_obj(conn: socket.socket, obj: dict) -> None:
    """
    Sends a JSON object to the client.
    """

    json_obj = json.dumps(obj)
    conn.sendall(json_obj.encode("utf-8"))


if __name__ == "__main__":
    s = Server(Path("server_data"))
    s.start()
