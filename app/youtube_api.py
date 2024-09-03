from app.ytdlp_utils import get_youtube_info
import yt_dlp as youtube_dl


def get_video_info(youtube_url: str):
    info = get_youtube_info(youtube_url)
    has_m4a = bool(
        next(
            (f for f in info["formats"] if f["ext"] == "m4a"),
            False,
        )
    )
    has_mp4 = bool(
        next(
            (f for f in info["formats"] if f["ext"] == "mp4"),
            False,
        )
    )

    return {
        "duration_s": info["duration"],
        "title": info["title"],
        "id": info["id"],
        "thumbnail": info["thumbnail"],
        "has_m4a": has_m4a,
        "has_mp4": has_mp4,
    }


def get_youtube_channel_videos(channel_url: str):
    ydl_opts = {
        "quiet": True,  # Keeps the output clean
        "extract_flat": True,  # Equivalent to --flat-playlist
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # Use the extract_info method to fetch the playlist information
        info = ydl.extract_info(channel_url, download=False)
        result = ydl.sanitize_info(info)

        return result
