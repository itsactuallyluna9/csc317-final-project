import sqlite3
from pathlib import Path
from threading import RLock
from typing import Optional

import bcrypt


def row_to_dict(row: sqlite3.Row) -> dict:
    """
    Convert a sqlite3.Row object to a dictionary.

    Args:
        row (sqlite3.Row): The row to convert.

    Returns:
        dict: The row as a dictionary.
    """
    return {key: row[key] for key in row.keys()}


class Database:
    MAX_ITEMS_PER_PAGE = 25  # client doesn't actually use this (and they don't want control over it), but needs it.

    def __init__(self, server_path: Path):
        """
        Initialize the database connection.

        Args:
            server_path (Optional[Path]): The path to the server directory. If None, uses the current directory. (The database is stored in server/db.sqlite3)
        """
        self.connection = sqlite3.connect(
            server_path / "db.sqlite3",
            check_same_thread=False,
        )
        self.connection.row_factory = sqlite3.Row
        self.lock = RLock()  # in case we need to use shenanigans :>
        self.cursor = self.connection.cursor()

    def get_users_page(self, page_num: int):
        """
        Get a page of users from the database.

        Args:
            page_num (int): The page number to retrieve.
        """
        with self.lock:
            users = self.cursor.execute(
                "SELECT username, joined_at, last_login FROM users LIMIT ? OFFSET ?",
                (self.MAX_ITEMS_PER_PAGE, page_num * self.MAX_ITEMS_PER_PAGE),
            ).fetchall()

            user_count = self.cursor.execute(
                "SELECT COUNT(*) FROM users",
            ).fetchone()[0]

        result = {
            "type": "USERS",
            "result": list(map(row_to_dict, users)),
            "current_page": page_num,
            "max_page": user_count // self.MAX_ITEMS_PER_PAGE,
            "items_per_page": self.MAX_ITEMS_PER_PAGE,
            "number_of_items": user_count,
        }

        return result

    def get_video_page(self, page_num: int, author_name: Optional[str] = None):
        """
        Get a page of videos from the database.

        Args:
            page_num (int): The page number to retrieve.
            author_name (Optional[str]): The name of the author to filter by. If None, retrieves all videos.
        """
        with self.lock:
            videos = self.cursor.execute(
                "SELECT title, id FROM videos WHERE author = ? LIMIT ? OFFSET ? AND length > 0",
                (
                    author_name,
                    self.MAX_ITEMS_PER_PAGE,
                    page_num * self.MAX_ITEMS_PER_PAGE,
                ),
            ).fetchall()

            video_count = self.cursor.execute(
                "SELECT COUNT(*) FROM videos WHERE author = ? AND length > 0",
                (author_name,),
            ).fetchone()[0]

        result = {
            "type": "VIDEOS",
            "result": list(map(row_to_dict, videos)),
            "current_page": page_num,
            "max_page": video_count // self.MAX_ITEMS_PER_PAGE,
            "items_per_page": self.MAX_ITEMS_PER_PAGE,
            "number_of_items": video_count,
        }

        return result

    def get_video_info(self, video_id: str):
        """
        Get information about a video from the database.

        Args:
            video_id (str): The ID of the video to retrieve.
        """
        with self.lock:
            video = self.cursor.execute(
                "SELECT * FROM videos WHERE id = ?", (video_id,)
            ).fetchone()

            return row_to_dict(video) if video else None

    def login(self, username: str, password: str) -> None:
        """
        Check if the username and password are valid.

        Args:
            username (str): The username to check.
            password (str): The password to check.
        """
        with self.lock:
            user = self.cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user is not None and bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        ):  # TODO: hash | checking hash using bcrypt
            return
        raise Exception("Invalid username or password")

    def register(self, username: str, password: str) -> None:
        """
        Register a new user in the database.

        Args:
            username (str): The username to register.
            password (str): The password to register.
        """
        with self.lock:
            user = self.cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            if user is not None:
                raise Exception("Username already exists")

            salt = bcrypt.gensalt()
            hashpw = bcrypt.hashpw(password.encode("utf-8"), salt)

            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (
                    username,
                    hashpw.decode("utf-8"),
                ),  # TODO: hash! | added hashing here, decodes at end to save in db as string
            )
            self.connection.commit()

    def start_upload_video(self, title: str, author: str) -> int:
        """
        Start the upload process for a video.

        Args:
            title (str): The title of the video.
            author (str): The author of the video.

        Returns:
            int: The ID of the video.
        """
        with self.lock:
            self.cursor.execute(
                "INSERT INTO videos (author, title, length, num_segments, max_quality) VALUES (?, ?, ?, ?, ?)",
                (author, title, -1.0, -1, -1),
            )
            self.connection.commit()
            return self.cursor.lastrowid or -1

    def update_video_info(
        self, video_id: int, length: float, num_segments: int, max_quality: int
    ) -> None:
        """
        Update the video information in the database. Basically, part 2 of the upload process.

        Args:
            video_id (int): The ID of the video.
            length (float): The length of the video.
            num_segments (int): The number of segments in the video.
            max_quality (int): The maximum quality of the video.
        """
        with self.lock:
            # print(f"Updating video info: {video_id}, {length}, {num_segments}, {max_quality}")
            self.cursor.execute(
                "UPDATE videos SET length = ?, num_segments = ?, max_quality = ? WHERE id = ?",
                (length, num_segments, max_quality, video_id),
            )
            self.connection.commit()
