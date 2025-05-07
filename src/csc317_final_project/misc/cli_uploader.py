import json
import socket
from pathlib import Path


def send_obj(conn: socket.socket, obj: dict) -> None:
    """
    Sends a JSON object to the client.
    """

    json_obj = json.dumps(obj)
    conn.sendall(json_obj.encode("utf-8"))


def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    video_path = input("Enter the path to the video file: ")
    title = input("Enter the title of the video: ")

    # Connect to the server
    server_address = ("localhost", 2121)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        print(f"Connected to server at {server_address}")

        # Send login credentials
        login_data = {
            "type": "LOGIN",
            "username": username,
            "password": password,
        }
        send_obj(s, login_data)

        # Wait for server response
        response = s.recv(1024)
        response_data = json.loads(response)
        if response_data.get("current_page") != 0:
            print("Login failed. Please check your username and password.")
            return
        print("Login successful.")
        # Send video upload request
        upload_data = {
            "type": "UPLOAD",
            "target": video_path,
            "file_size": Path(video_path).stat().st_size,
            "title": title,
        }
        send_obj(s, upload_data)

        response = s.recv(1024)
        if response != b'{"type": "ACK"}':
            print("Server did not acknowledge video upload request - What?")
            print(response)
            return
        print("Video upload request acknowledged. Starting upload...")
        with open(video_path, "rb") as file:
            s.sendfile(file)
        print("Video upload completed successfully.")


if __name__ == "__main__":
    main()
