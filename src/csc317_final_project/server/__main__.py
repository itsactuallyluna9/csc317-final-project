import json
import socket
import threading
from logging import getLogger
from pathlib import Path
from time import sleep
from typing import Optional, Tuple

from csc317_final_project.server.db import Database
from csc317_final_project.server.ffmpeg import process_video
from csc317_final_project.server.fs import (
    get_segment_path,
    get_video_root_path,
)
from csc317_final_project.server.quality import VideoQuality

SEGMENT_SIZE = 4096

logger = getLogger(__name__)


class ClientState:
    """
    Holds state for each client, created so multiple clients can have their own current working directory
    """

    def __init__(self, conn: socket.socket, addr: Tuple[str, int]):
        self.conn = conn
        self.addr = addr
        self.username = None


class Server:
    def __init__(
        self, server_path: Path, host: str = "0.0.0.0", port: int = 2121
    ) -> None:
        self.host = host
        self.port = port
        self.path = server_path
        self.db = Database(server_path)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.server.bind((self.host, self.port))
                break
            except OSError:
                logger.warning(
                    f"Port {self.port} is already in use. Waiting for a bit..."
                )
                sleep(5)

    def start(self) -> None:
        """
        Start the server and listen for incoming connections.

        This method will run indefinitely, accepting new connections and spawning a new thread for each client.
        """
        self.server.listen()
        logger.info(f"Server is listening on HOST = {self.host}, PORT = {self.port}")
        try:
            while True:
                conn, addr = self.server.accept()
                logger.debug(f"Accepted connection from {addr}")
                client_state = ClientState(conn, addr)
                thread = threading.Thread(
                    target=self.handle_client, args=(client_state,), daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.server.close()
            logger.info("Server socket closed.")

    def handle_client(self, client: ClientState) -> None:
        """
        Handle a client connection.
        """

        while True:
            packet = client.conn.recv(SEGMENT_SIZE).decode("utf-8")
            if not packet:
                break
            recieved_obj = json.loads(packet)
            logger.debug(f"Received message from {client.addr}: {recieved_obj}")
            try:
                to_client = self.handle_command(client, recieved_obj)
                if to_client:
                    send_obj(client.conn, to_client)
            except Exception as e:
                logger.error(f"Error handling command for client {client.addr}: {e}")
                send_obj(
                    client.conn,
                    {
                        "type": "ERROR",
                        "message": str(e),
                    },
                )

        client.conn.close()

    def handle_command(self, client: ClientState, recieved_obj: dict) -> Optional[dict]:
        # handling to upload, modify videos
        # data handling for clients gui and actions below
        if recieved_obj["type"] == "LOGIN":
            self.db.login(
                recieved_obj["username"],
                recieved_obj["password"],
            )
            # they want the first page of users on successful login
            # so...
            client.username = recieved_obj["username"]
            return self.handle_command(
                client,
                {
                    "type": "USERS",
                    "page_num": 0,
                },
            )

        elif recieved_obj["type"] == "LOGOUT":
            client.username = None
            return {
                "success": True,
            }

        elif recieved_obj["type"] == "REGISTER":
            self.db.register(
                recieved_obj["username"],
                recieved_obj["password"],
            )

            # they want the first page of users on successful login/register
            # so...
            return self.handle_command(
                client,
                {
                    "type": "USERS",
                    "page_num": 0,
                },
            )

        elif recieved_obj["type"] == "USERS":
            # get the users from the database
            page_num = recieved_obj["page_num"]
            users = self.db.get_users_page(page_num)
            return users

        elif recieved_obj["type"] == "VIDEO":
            # segments - download!!
            return download(
                client.conn,
                get_segment_path(
                    self.path,
                    recieved_obj["video_id"],
                    VideoQuality(recieved_obj["quality"]),
                    recieved_obj["segment_id"],
                ),
            )

        elif recieved_obj["type"] == "VIDEO_UPLOAD":
            # upload!!!
            if client.username is None:
                raise Exception("Client not logged in")
            file_ext = Path(recieved_obj["target"]).suffix
            title = recieved_obj["title"]
            file_size = recieved_obj["file_size"]
            video_id = self.db.start_upload_video(title, client.username)
            video_root = get_video_root_path(self.path, str(video_id))
            video_root.mkdir(parents=True, exist_ok=True)
            original_video = video_root / f"original{file_ext}"
            upload(client.conn, original_video, file_size)
            process_video(original_video)
            return {"success": True}

        elif recieved_obj["type"] == "VIDEO_INFO":
            # get the video info from the database
            video_id = recieved_obj["video_id"]
            video_info = self.db.get_video_info(video_id)
            return video_info

        elif recieved_obj["type"] == "VIDEO_PAGE":
            # get the videos from the database
            page_num = recieved_obj["page_num"]
            author = recieved_obj.get("author", None)
            videos = self.db.get_video_page(page_num, author)
            return videos

        else:
            raise NotImplementedError(
                f"Command {recieved_obj['type']} not implemented yet!! :<"
            )


def upload(conn: socket.socket, file_path: Path, file_size: int) -> None:
    """
    Handle file upload from client.
    """

    send_obj(conn, {"type": "ACK"})
    completed = 0
    with file_path.open("wb") as f:
        while completed < file_size:
            data = conn.recv(SEGMENT_SIZE)
            f.write(data)
            completed += len(data)
    logger.debug(
        f"File with name {file_path.name} by the user {conn.getpeername()[0]} uploaded to the server."
    )


def download(conn: socket.socket, file_path: Path) -> None:
    """
    Handle file download to client.
    """

    # personally, i love the pathlib api
    # so im using it because there's enough to worry about already
    if not file_path.is_file():  # also checks if it exists
        # we can't send!!!
        raise FileNotFoundError(f"File not found at target path {file_path}")

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

    ack = json.loads(conn.recv(SEGMENT_SIZE))  # check for ACK from client
    if ack != {"type": "ACK"}:
        raise RuntimeError(f"Client did not acknowledge file transfer. Received: {ack}")

    # now we can send the file
    with open(file_path, "rb") as file:
        while True:
            data = file.read(SEGMENT_SIZE)
            if not data:
                break
            conn.sendall(data)

    # and we're done, the client will know when we're done (because of the file_size we sent earlier)
    logger.debug(
        f"File {file_path} sent to client @ {conn.getpeername()[0]}"
    )  # this is the ip of the client, not the server


def send_obj(conn: socket.socket, obj: dict) -> None:
    """
    Sends a JSON object to the client.
    """

    json_obj = json.dumps(obj)
    conn.sendall(json_obj.encode("utf-8"))


def main():
    import logging

    logging.basicConfig(
        format="%(asctime)s - %(name)s (%(threadName)s) - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    s = Server(Path("server_data"))
    s.start()


if __name__ == "__main__":
    main()
