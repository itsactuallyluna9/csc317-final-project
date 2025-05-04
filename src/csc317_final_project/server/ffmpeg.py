"""
This module provides functionality to convert video files using FFmpeg.

Abandon all hope, all ye who enter here. ~Luna
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from logging import getLogger
from concurrent.futures import ThreadPoolExecutor
from platform import processor, system

logger = getLogger(__name__)


def does_ffmpeg_exist() -> bool:
    """
    Check if FFmpeg is installed on the system.

    Returns:
        bool: True if FFmpeg is installed, False otherwise.
    """
    try:
        logger.debug("Checking if FFmpeg is installed...")
        subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except FileNotFoundError:
        return False


def get_video_info(video_path: Path) -> Dict:
    """
    Get information about a video file using FFprobe.

    Args:
        video_path (Path): The path to the video file.

    Returns:
        Dict: A dictionary containing video information.
    """
    try:
        logger.debug(f"Getting video info for: {video_path}")
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=width,height,r_frame_rate,codec_name,duration",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(video_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )

        info = json.loads(result.stdout)

        # extract video stream info
        video_stream = None
        for stream in info.get("streams", []):
            if "width" in stream and "height" in stream:
                video_stream = stream
                break

        if not video_stream:
            logger.error("No video stream found in the file.")
            return {}

        if "r_frame_rate" in video_stream:
            try:
                num, denom = map(int, video_stream["r_frame_rate"].split("/"))
                fps = num / denom
            except (ValueError, ZeroDivisionError):
                fps = 30  # fallback
        else:
            fps = 30
        duration = float(video_stream.get("duration", 0)) or float(
            info.get("format", {}).get("duration", 0)
        )

        return {
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "fps": fps,
            "codec": video_stream.get("codec_name"),
            "duration": duration,
        }

    except (subprocess.SubprocessError, json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error getting video info: {e}")
        return {}


def convert_video(
    input_file: Path,
    output_file: Path,
    target_height: int,
    name: str,
    crf: int,
    preset: str,
    video_bitrate: str,
    audio_bitrate: str,
    segment_length: float,
) -> None:
    """
    Convert a video file to a specified format and quality. Also splits the video into segments.

    Args:
        input_file (Path): The path to the input video file.
        output_file (Path): The path to the output video file, as a stem and extension. ("output.mp4" will turn into "outputXYZ.mp4", where XYZ is the segment number)
        target_height (int): The target height for the video.
        name (str): The preset name (e.g., "4K", "2K", "1080p", etc.).
        crf (int): The constant rate factor for the video encoding.
        preset (str): The encoding preset for FFmpeg.
        video_bitrate (str): The video bitrate for the output file.
        audio_bitrate (str): The audio bitrate for the output file.
        segment_length (float): The length of each segment in seconds. (Approximate - video may not split exactly at this length)
    """
    logger.info(
        f"Converting video: {input_file} to {output_file} with target height {target_height}"
    )

    if system() == "Darwin" and processor() == "arm":
        # we're running on the m serires: use the hardware acceleration
        logger.debug("Using Apple silicon hardware acceleration.")
        hw_accel = "h264_videotoolbox"
    else:
        # unknown! use the software encoder
        # there's more hardware acceleration stuff, but... i'm the one running this,
        # so i really only care about my system.
        logger.debug("Using software encoding - good luck.")
        hw_accel = "libx264"
    # Alright this command's a bit of a mess, but:
    # It takes the input file, re-encodes it (video with libx264 w/preset and crf; audio with aac),
    # with the max bitrate set to the video_bitrate, and the audio bitrate set to audio_bitrate.
    # Also: rescales the video to the target height (adjusting width to maintain aspect ratio)
    # and splits the video into segments of segment_length seconds (with the segment number appended to the filename).
    process = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(input_file),
            "-c:v",
            hw_accel,
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-maxrate",
            video_bitrate,
            "-vf",
            f"scale=-1:{target_height}",
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate,
            "-movflags",
            "+faststart",
            "-f",
            "segment",
            "-segment_time",
            str(segment_length),
            f"{output_file.stem}%03d{output_file.suffix}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        logger.error(f"FFmpeg error: {process.stderr}")
        raise RuntimeError(
            f"FFmpeg failed with error: {process.stderr.decode('utf-8')}"
        )
    logger.info(f"Video {input_file} converted to {output_file}")


def generate_thumbnail(
    video: Path, output_file: Path, video_position: float = 0.3
) -> None:
    """
    Generate a thumbnail for a video file using FFmpeg. (Around 30% into the video by default)

    Args:
        video (Path): The path to the input video file.
        output_file (Path): The path to the output thumbnail image file.
        video_position (float, optional): The position in the video to capture the thumbnail. Defaults to 0.3 (30% into the video).
    """
    video_position = min(max(video_position, 0), 1)  # clamp between 0 and 1
    video_info = get_video_info(video)
    if not video_info:
        logger.error("Failed to get video info.")
        raise RuntimeError("Failed to get video info.")
    duration = video_info.get("duration", 0)
    if duration <= 0:
        logger.error("Invalid video duration.")
        raise RuntimeError("Invalid video duration.")
    time = duration * video_position  # 30% into the video
    process = subprocess.run(
        [
            "ffmpeg",
            "-ss",
            str(time),
            "-i",
            str(video),
            "-vframes",
            "1",
            "-q:v",
            "2",
            str(output_file),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        logger.error(f"FFmpeg error: {process.stderr}")
        raise RuntimeError(
            f"FFmpeg failed with error: {process.stderr.decode('utf-8')}"
        )
    logger.info(f"Thumbnail generated: {output_file}")


def process_video(video: Path, max_workers: Optional[int] = 2) -> None:
    """
    Process an uploaded video file, converting it to a more compatible format and splitting into segments.

    Will block until the process is complete. This *will* take a while.

    Args:
        video (Path): The path to the video file to be processed.
        max_workers (int, optional): The maximum number of threads to use for processing. Defaults to 2.
    """
    logger.info(f"Processing video: {video}")
    if not does_ffmpeg_exist():
        logger.critical("FFmpeg is not installed.")
        raise RuntimeError("FFmpeg is not installed.")

    video_info = get_video_info(video)
    if not video_info:
        logger.error("Failed to get video info.")
        raise RuntimeError("Failed to get video info.")
    source_height = video_info.get("height", 0)

    resolution_configs = [
        # height, name, crf(constant rate factor - lower is better)
        # preset, video bitrate, audio bitrate
        (2160, "4K", 16, "slow", "16000k", "192k"),
        (1440, "2K", 23, "slow", "8000k", "128k"),
        (1080, "1080p", 23, "slow", "5000k", "128k"),
        (720, "720p", 23, "slow", "2500k", "128k"),
        (480, "480p", 23, "slow", "1000k", "128k"),
        (360, "360p", 23, "slow", "500k", "128k"),
        (240, "240p", 23, "slow", "300k", "128k"),
        (144, "144p", 23, "slow", "100k", "128k"),
    ]

    valid_configs = [cfg for cfg in resolution_configs if cfg[0] <= source_height]
    if not valid_configs:
        logger.error("No valid resolution configurations found.")
        raise RuntimeError("No valid resolution configurations found.")

    # note that, for scalability, we should really be using a separate worker process
    # and we'll submit the videos to a queue that will then be processed by the worker.
    # for now, though, this is fine.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for height, name, crf, preset, video_bitrate, audio_bitrate in valid_configs:
            output_file = video.parent / f"{video.stem}_{name}{video.suffix}"
            executor.submit(
                convert_video,
                video,
                output_file,
                height,
                name,
                crf,
                preset,
                video_bitrate,
                audio_bitrate,
                1000000000,  # segment length in seconds
            )


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    generate_thumbnail(
        Path("sys_on_fys_final.mp4"),
        Path("sys_on_fys_final_thumbnail.jpg"),
    )
    # process_video(Path("sys_on_fys_final.mp4"), None)
