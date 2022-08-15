import os
import json
import logging

import aiohttp_cors
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
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".mp4": "application/octet-stream",
    ".m4s": "application/octet-stream",
}

async def get_video_list(request):
    folder_list = os.listdir(BASE_STREAM_DIR_PATH)
    video_list = []

    for folder_name in folder_list:
        _temp_video = {
            "name": folder_name
        }
        with open(os.path.join(BASE_STREAM_DIR_PATH, folder_name, "info.json"), "r") as f:
            _data = json.load(f)
            _temp_video.update(_data)
        video_list.append(_temp_video)
    return web.json_response(video_list)

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

async def handle_stream_m3u8(request):
    video_name = request.match_info.get("video_name", "")
    file_path = os.path.join(BASE_STREAM_DIR_PATH, video_name, "stream.m3u8")
    headers = {
        "Content-Type": CONTENT_TYPE_MAP[".m3u8"],
    }
    with open(file_path, "rb") as file:
        body = file.read()
    return web.Response(body=body, headers=headers)

if __name__ == '__main__':
    print(f"{HOST}:{PORT} -> {BASE_STREAM_DIR_PATH}")
    app = web.Application()
    cors = aiohttp_cors.setup(app)
    cors.add(app.router.add_get("/streams/{video_name}/{filename}", handle_stream), {"*":
            aiohttp_cors.ResourceOptions(allow_credentials=False)})
    cors.add(app.router.add_get("/streams_m3u8/{video_name}/", handle_stream_m3u8), {"*":
            aiohttp_cors.ResourceOptions(allow_credentials=False)})
    cors.add(app.router.add_get("/streams_m3u8/{video_name}/{filename}", handle_stream), {"*":
            aiohttp_cors.ResourceOptions(allow_credentials=False)})
    cors.add(app.router.add_get("/streams/get_video_list", get_video_list), {"*":
            aiohttp_cors.ResourceOptions(allow_credentials=False)})
    web.run_app(app, host=HOST, port=PORT)