from typing import Any, Tuple
import yt_dlp as youtube_dl


class YoutubeLengthException(Exception):
    pass


def get_youtube_info(youtube_url: str) -> dict[str, Any]:
    info_loader = youtube_dl.YoutubeDL()
    try:
        info = info_loader.extract_info(youtube_url, download=False)
        if not info:
            raise Exception("No video found")
        return info
    except youtube_dl.utils.DownloadError as err:
        raise Exception(str(err))


def get_youtube_length_s_from_info(info: dict[str, Any]) -> int:
    file_length = info["duration_string"]
    file_h_m_s = file_length.split(":")
    file_h_m_s = [int(sub_length) for sub_length in file_h_m_s]

    if len(file_h_m_s) == 1:
        file_h_m_s.insert(0, 0)
    if len(file_h_m_s) == 2:
        file_h_m_s.insert(0, 0)
    file_length_s = file_h_m_s[0] * 3600 + file_h_m_s[1] * 60 + file_h_m_s[2]
    return file_length_s


def get_youtube_info_and_length_s(youtube_url: str) -> Tuple[dict[str, Any], int]:
    info = get_youtube_info(youtube_url)
    file_length_s = get_youtube_length_s_from_info(info)
    return info, file_length_s
