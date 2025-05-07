"""
File system utilities for the server.
"""

from pathlib import Path

from csc317_final_project.server.quality import VideoQuality


def get_segment_path(
    server_path: Path,
    video_id: int,
    quality: VideoQuality,
    segment_id: int,
) -> Path:
    """
    Get the path to a video segment.

    Args:
        server_path (Path): The path to the server directory.
        video_id (int): The ID of the video.
        quality (VideoQuality): The quality of the video.
        segment_id (int): The ID of the segment.

    Returns:
        Path: The path to the video segment.
    """
    return (
        get_video_root_path(server_path, str(video_id)) / str(quality) / f"{video_id}_{str(quality.value)}_{segment_id}.mp4"
    )


def get_thumbnail_path(server_path: Path, video_id: str) -> Path:
    """
    Get the path to a video thumbnail.

    Args:
        server_path (Path): The path to the server directory.
        video_id (str): The ID of the video.

    Returns:
        Path: The path to the video thumbnail.
    """
    return get_video_root_path(server_path, video_id) / "thumbnail.jpg"


def get_original_video_path(server_path: Path, video_id: str) -> Path:
    """
    Get the path to the originally uploaded video, as uploaded by the user.

    Args:
        server_path (Path): The path to the server directory.
        video_id (str): The ID of the video.

    Returns:
        Path: The path to the originally uploaded video.
    """
    # as it can be of any extension, we need to find original*
    video_dir = get_video_root_path(server_path, video_id)
    for file in video_dir.glob("original.*"):
        return file
    return video_dir / "original.mp4"  # fallback to mp4 if not found


def get_video_root_path(server_path: Path, video_id: str) -> Path:
    """
    Get the path to a video.

    Args:
        server_path (Path): The path to the server directory.
        video_id (str): The ID of the video.

    Returns:
        Path: The path to the video.
    """
    return server_path / "videos" / video_id
