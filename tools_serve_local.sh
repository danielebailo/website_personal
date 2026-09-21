#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 tools_update_youtube_videos.py
exec hugo server -D --disableFastRender --bind 127.0.0.1 --port "${PORT:-1314}"
