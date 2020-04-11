import os
import logging

from aiohttp import web
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BASE_STREAM_DIR_PATH = os.getenv("BASE_STREAM_DIR_PATH")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
CONTENT_TYPE_MAP = {
    ".m3u8": "application/vnd.apple.mpegurl",
    ".ts": "video/mp2t",
}

async def handle_stream(request):
    video_name = request.match_info.get("video_name", "")
    filename = request.match_info.get("filename", "")
    _, file_extension = os.path.splitext(filename)
    file_path = os.path.join(BASE_STREAM_DIR_PATH, video_name, filename)

    try:
        headers = {
            "Content-Type": CONTENT_TYPE_MAP[file_extension],
        }
    except Exception as e:
        logger.error(e)
        raise web.HTTPBadRequest(body=f"Unsupported file: {e}")

    if not os.path.exists(file_path):
        raise web.HTTPBadRequest(body=f"Video name not exists")

    with open(file_path, "rb") as file:
        body = file.read()
    return web.Response(body=body, headers=headers)

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get("/streams/{video_name}/{filename}", handle_stream)
    web.run_app(app, host=HOST, port=PORT)