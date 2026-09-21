from pathlib import Path
import json
import re
import urllib.request

CHANNEL_URL = 'https://www.youtube.com/@danielebailo/videos'
OUT = Path('data/youtube_videos.json')


def extract_initial_data(html: str):
    m = re.search(r'ytInitialData\s*=\s*', html)
    if not m:
        raise RuntimeError('ytInitialData not found')
    start = html.find('{', m.end())
    depth = 0
    in_str = False
    esc = False
    end = None
    for i, ch in enumerate(html[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    if end is None:
        raise RuntimeError('ytInitialData JSON end not found')
    return json.loads(html[start:end])


def walk(obj):
    if isinstance(obj, dict):
        if 'lockupViewModel' in obj:
            yield obj['lockupViewModel']
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def get_nested(obj, path, default=None):
    cur = obj
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def extract_duration(lockup):
    label = get_nested(lockup, ['rendererContext', 'accessibilityContext', 'label'], '') or ''
    # Keep the visible short duration when YouTube exposes it on the badge.
    badges = get_nested(lockup, ['contentImage', 'thumbnailViewModel', 'overlays'], []) or []
    for overlay in badges:
        badge = get_nested(overlay, ['thumbnailBottomOverlayViewModel', 'badges', 0, 'thumbnailBadgeViewModel', 'text'])
        if badge:
            return badge
    m = re.search(r'(\d+\s+(?:minuti?|ore?)\s+e\s+\d+\s+secondi|\d+\s+secondi)', label)
    return m.group(1) if m else ''


def main():
    req = urllib.request.Request(CHANNEL_URL, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    data = extract_initial_data(html)

    videos = []
    seen = set()
    for lockup in walk(data):
        video_id = lockup.get('contentId')
        if not video_id or video_id in seen:
            continue
        title = get_nested(lockup, ['metadata', 'lockupMetadataViewModel', 'title', 'content'], '')
        if not title:
            continue
        metadata_rows = get_nested(lockup, ['metadata', 'lockupMetadataViewModel', 'metadata', 'contentMetadataViewModel', 'metadataRows'], []) or []
        meta = []
        for row in metadata_rows:
            for part in row.get('metadataParts', []):
                text = get_nested(part, ['text', 'content'])
                if text:
                    meta.append(text)
        videos.append({
            'id': video_id,
            'title': title,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
            'duration': extract_duration(lockup),
            'meta': ' · '.join(meta),
        })
        seen.add(video_id)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(videos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {len(videos)} videos to {OUT}')


if __name__ == '__main__':
    main()
