from enum import IntEnum


class VideoQuality(IntEnum):
    FOUR_K = 7
    TWO_K = 6
    ONE_K = 5
    SEVEN_TWENTY_P = 4
    FOUR_EIGHTY_P = 3
    THREE_SIXTY_P = 2
    TWO_FORTY_P = 1
    ONE_FORTY_FOUR_P = 0

    def __str__(self):
        if self == VideoQuality.FOUR_K:
            return "4K"
        elif self == VideoQuality.TWO_K:
            return "2K"
        elif self == VideoQuality.ONE_K:
            return "1080p"
        elif self == VideoQuality.SEVEN_TWENTY_P:
            return "720p"
        elif self == VideoQuality.FOUR_EIGHTY_P:
            return "480p"
        elif self == VideoQuality.THREE_SIXTY_P:
            return "360p"
        elif self == VideoQuality.TWO_FORTY_P:
            return "240p"
        elif self == VideoQuality.ONE_FORTY_FOUR_P:
            return "144p"
        else:
            return "Unknown"

    def get_resolution_config(self):
        # height, name, crf(constant rate factor - lower is better)
        # preset, video bitrate, audio bitrate
        if self == VideoQuality.FOUR_K:
            return (2160, "4K", 16, "slow", "16000k", "192k")
        elif self == VideoQuality.TWO_K:
            return (1440, "2K", 23, "slow", "8000k", "128k")
        elif self == VideoQuality.ONE_K:
            return (1080, "1080p", 23, "slow", "5000k", "128k")
        elif self == VideoQuality.SEVEN_TWENTY_P:
            return (720, "720p", 23, "slow", "2500k", "128k")
        elif self == VideoQuality.FOUR_EIGHTY_P:
            return (480, "480p", 23, "slow", "1000k", "128k")
        elif self == VideoQuality.THREE_SIXTY_P:
            return (360, "360p", 23, "slow", "500k", "128k")
        elif self == VideoQuality.TWO_FORTY_P:
            return (240, "240p", 23, "slow", "300k", "128k")
        elif self == VideoQuality.ONE_FORTY_FOUR_P:
            return (144, "144p", 23, "slow", "100k", "128k")
        else:
            return None

    def get_video_height(self):
        if self == VideoQuality.FOUR_K:
            return 2160
        elif self == VideoQuality.TWO_K:
            return 1440
        elif self == VideoQuality.ONE_K:
            return 1080
        elif self == VideoQuality.SEVEN_TWENTY_P:
            return 720
        elif self == VideoQuality.FOUR_EIGHTY_P:
            return 480
        elif self == VideoQuality.THREE_SIXTY_P:
            return 360
        elif self == VideoQuality.TWO_FORTY_P:
            return 240
        elif self == VideoQuality.ONE_FORTY_FOUR_P:
            return 144
        else:
            return -1
