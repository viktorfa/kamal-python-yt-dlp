import re
import subprocess
from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
import yt_dlp as youtube_dl
from app.youtube_api import get_video_info, get_youtube_channel_videos

app = FastAPI()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred"},
    )


api_v1_router = APIRouter(prefix="/api/v1")


@api_v1_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_v1_router.get("/video_info/")
async def video_info(
    youtube_url: str = Query(..., description="The URL of the YouTube video"),
):
    yt_info = get_video_info(youtube_url=youtube_url)
    return {"yt_info": yt_info}


@api_v1_router.get("/playlist_info/")
async def playlist_info(
    channel_url: str = Query(..., description="The URL of the YouTube video"),
):
    channel_info = get_youtube_channel_videos(channel_url=channel_url)
    return {"channel_info": channel_info}


def determine_media_type_and_format(format_string: str):
    # Extract the 'ext' from the format string using regex
    ext_match = re.search(r"\[ext=([^\]]+)\]", format_string)

    # Determine if it's audio or video based on the keywords "audio" or "video"
    if "audio" in format_string:
        media_type = "audio"
    elif "video" in format_string:
        media_type = "video"
    else:
        media_type = "application/octet-stream"  # Fallback if type is unclear

    # Default format is the extracted extension or unknown if not found
    ext = ext_match.group(1) if ext_match else "unknown"

    return f"{media_type}/{ext}"


def stream_youtube_video(url: str, format: str):
    ydl_opts = {
        "format": format,
        "noplaylist": True,
        "quiet": True,
        "outtmpl": "-",  # Use a hyphen to send the output to stdout
    }

    def generate():
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            if not result:
                raise Exception("No video found")

            requested_format = (
                result["requested_formats"][0]
                if "requested_formats" in result
                else result
            )

            # Command to download and stream the video/audio
            command = [
                "yt-dlp",
                "-f",
                format,
                "-o",
                "-",
                url,
            ]

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            try:
                while True:
                    data = process.stdout.read(1024)  # Read in chunks
                    if not data:
                        break
                    yield data
            finally:
                process.stdout.close()
                process.stderr.close()
                process.wait()

    # Determine the media type based on the format
    if "audio" in format:
        media_type = determine_media_type_and_format(format)
    elif "video" in format:
        media_type = determine_media_type_and_format(format)
    else:
        media_type = "application/octet-stream"  # Fallback if the type is unclear

    return StreamingResponse(generate(), media_type=media_type)


@api_v1_router.get("/stream")
async def stream_media(youtube_url: str, format: str):
    return stream_youtube_video(youtube_url, format)


@app.get("/up")
async def up():
    return {"status": "OK"}


app.include_router(api_v1_router)
