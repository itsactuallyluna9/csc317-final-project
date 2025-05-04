import sqlite3
from threading import RLock
from pathlib import Path
from typing import Optional


def row_to_dict(row):
    """
    Convert a sqlite3.Row object to a dictionary.

    Args:
        row (sqlite3.Row): The row to convert.

    Returns:
        dict: The row as a dictionary.
    """
    return {key: value for key, value in row.items()}


class Database:
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
        USERS_PER_PAGE = 25  # client doesn't actually use this (and they don't want control over it), but needs it.

        with self.lock:
            users = self.cursor.execute(
                "SELECT username, joined_at, last_login FROM users LIMIT ? OFFSET ?",
                (USERS_PER_PAGE, page_num * USERS_PER_PAGE),
            ).fetchall()

            user_count = self.cursor.execute(
                "SELECT COUNT(*) FROM users",
            ).fetchone()[0]

        result = {
            "result": list(map(row_to_dict, users)),
            "current_page": page_num,
            "max_page": user_count // USERS_PER_PAGE,
            "videos_per_page": USERS_PER_PAGE,
            "number_of_videos": user_count,
        }

        return result

    def get_video_page(self, page_num: int, author_name: Optional[str] = None):
        """
        Get a page of videos from the database.

        Args:
            page_num (int): The page number to retrieve.
            author_name (Optional[str]): The name of the author to filter by. If None, retrieves all videos.
        """
        VIDEOS_PER_PAGE = 25  # client doesn't actually use this (and they don't want control over it), but needs it.

        with self.lock:
            videos = self.cursor.execute(
                "SELECT title, id FROM videos WHERE author = ? LIMIT ? OFFSET ?",
                (author_name, VIDEOS_PER_PAGE, page_num * VIDEOS_PER_PAGE),
            ).fetchall()

            video_count = self.cursor.execute(
                "SELECT COUNT(*) FROM videos WHERE author = ?", (author_name,)
            ).fetchone()[0]

        result = {
            "result": list(map(row_to_dict, videos)),
            "current_page": page_num,
            "max_page": video_count // VIDEOS_PER_PAGE,
            "videos_per_page": VIDEOS_PER_PAGE,
            "number_of_videos": video_count,
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

    def login(self, username: str, password: str) -> bool:
        """
        Check if the username and password are valid.

        Args:
            username (str): The username to check.
            password (str): The password to check.

        Returns:
            bool: True if the username and password are valid, False otherwise.
        """
        with self.lock:
            user = self.cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            return user is not None and user["password"] == password  # TODO: hash this

    def register(self, username: str, password: str) -> bool:
        """
        Register a new user in the database.

        Args:
            username (str): The username to register.
            password (str): The password to register.

        Returns:
            bool: True if the registration was successful, False otherwise.
        """
        with self.lock:
            user = self.cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            if user is not None:
                return False
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),  # TODO: hash!
            )
            self.connection.commit()
            return True
