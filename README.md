# Stream server

## Introduction

Now only support HLS(HTTP Live Streaming)

## Setup

Create .env file

```text
BASE_STREAM_DIR_PATH={stream folder path}
HOST={host}
PORT={port}
```

FFmpeg cmd: convert mp4 to m3u8 and ts

```shell
$ ffmpeg -i test.mp4 -c:v h264 -crf 21 -preset veryfast -c:a aac -b:a 128k -ac 2 -start_number 0 -hls_time 6 -hls_playlist_type event -f hls stream.m3u8
```

## Start

```shell
$ python server.py
```

stream folder structure:

```
 └─test
    ├─title
    ├─stream.m3u8
    └─stream.ts

```

try connect http://127.0.0.1:8080/streams/test/stream.m3u8  
try connect http://127.0.0.1:8080/streams/get_video_list  