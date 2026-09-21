from pathlib import Path
from lxml import etree as ET
from markdownify import markdownify as md
import yaml, re, html, shutil, urllib.parse

XML = Path('/Users/danielebailo/.pi/tmp/wordpress-export/SITO MUSICALE/danielebailomusic.WordPress.2026-09-14.xml')
UPLOADS = Path('/Users/danielebailo/.pi/tmp/wordpress-export/SITO MUSICALE/uploads')
FALLBACK_UPLOADS = Path('/Users/danielebailo/.pi/tmp/wordpress-export/uploads')
SITE = Path('/Users/danielebailo/Documents/PROJ.SRC/github/website_personal')
BLOG = SITE / 'content' / 'blog'
STATIC_UPLOADS = SITE / 'static' / 'uploads'
REPORT = SITE / 'MIGRATION_REPORT_MUSIC.md'

ns = {
    'wp':'http://wordpress.org/export/1.2/',
    'content':'http://purl.org/rss/1.0/modules/content/',
    'excerpt':'http://wordpress.org/export/1.2/excerpt/',
}
parser=ET.XMLParser(recover=True, huge_tree=True)
root=ET.parse(str(XML), parser).getroot()
items=root.xpath('./channel/item')

def gettext(item, path, namespaces=None):
    return (item.findtext(path, namespaces=namespaces or {}) or '').strip()

def slugify(value):
    value = urllib.parse.unquote(value or '')
    value = value.strip('/').split('/')[-1]
    value = re.sub(r'\.html?$', '', value)
    value = value.lower()
    value = value.translate(str.maketrans({'à':'a','è':'e','é':'e','ì':'i','ò':'o','ù':'u','ç':'c'}))
    value = re.sub(r'[^a-z0-9]+', '-', value).strip('-')
    return value or 'post'

def normalize_upload_ref(ref):
    ref = html.unescape(ref).split('?')[0].rstrip('.,;')
    ref = urllib.parse.unquote(ref)
    return ref.lstrip('/')

primary_upload_files = [p for p in UPLOADS.rglob('*') if p.is_file()]
fallback_upload_files = [p for p in FALLBACK_UPLOADS.rglob('*') if p.is_file()] if FALLBACK_UPLOADS.exists() else []
all_upload_files = primary_upload_files + fallback_upload_files
upload_by_name = {}
upload_by_path = {}
upload_source_by_rel = {}
for root_dir, files in [(UPLOADS, primary_upload_files), (FALLBACK_UPLOADS, fallback_upload_files)]:
    for p in files:
        rel = str(p.relative_to(root_dir))
        upload_by_name.setdefault(p.name.lower(), rel)
        upload_by_path.setdefault(rel.lower(), rel)
        upload_source_by_rel.setdefault(rel, p)

def resolve_upload_ref(ref):
    ref = normalize_upload_ref(ref)
    if (UPLOADS / ref).exists():
        return ref
    if ref.lower() in upload_by_path:
        return upload_by_path[ref.lower()]
    return upload_by_name.get(Path(ref).name.lower(), ref)

def local_upload_url(ref):
    return '/uploads/' + resolve_upload_ref(ref).replace(' ', '%20')

def refs_from_text(text):
    refs=set()
    patterns = [
        r'https?://(?:www\.)?danielebailo\.it/music/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://(?:www\.)?danielebailo\.it/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://i\d\.wp\.com/www\.danielebailo\.it/music/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://i\d\.wp\.com/www\.danielebailo\.it/wp-content/uploads/([^\s"\'<>\)]+)',
    ]
    for pattern in patterns:
        for u in re.findall(pattern, text or ''):
            refs.add(resolve_upload_ref(u))
    return refs

def protect_embeds(content):
    embeds = []
    def repl(m):
        raw = re.sub(r'\s+', ' ', m.group(0)).strip()
        token = f'PIEMBEDTOKEN{len(embeds)}X'
        embeds.append(raw)
        return f'\n\n{token}\n\n'
    content = re.sub(r'<iframe\b[^>]*>.*?</iframe>', repl, content or '', flags=re.I|re.S)
    return content, embeds

def restore_embeds(body, embeds):
    for i, raw in enumerate(embeds):
        body = body.replace(f'PIEMBEDTOKEN{i}X', f'\n\n<div class="media-embed">{raw}</div>\n\n')
    return body

def youtube_embed(url):
    url = html.unescape(url or '').strip().replace('\\_', '_')
    video_id = ''
    for pattern in [r'youtube\.com/embed/([A-Za-z0-9_-]+)', r'youtube\.com/watch\?v=([A-Za-z0-9_-]+)', r'youtu\.be/([A-Za-z0-9_-]+)']:
        m = re.search(pattern, url)
        if m:
            video_id = m.group(1)
            break
    if not video_id:
        return url
    return f'\n\n<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{video_id}" title="YouTube video" loading="lazy" allowfullscreen></iframe></div>\n\n'

def rewrite_content(content):
    content = content or ''
    for pattern in [
        r'https?://(?:www\.)?danielebailo\.it/music/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://(?:www\.)?danielebailo\.it/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://i\d\.wp\.com/www\.danielebailo\.it/music/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://i\d\.wp\.com/www\.danielebailo\.it/wp-content/uploads/([^\s"\'<>\)]+)',
    ]:
        content = re.sub(pattern, lambda m: local_upload_url(m.group(1)), content)
    content = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', r'\n\n\1\n\n', content, flags=re.I|re.S)
    return content

def cleanup_markdown(body):
    body = body.replace('\xa0', ' ')
    body = re.sub(r'\[embed[^\]]*\](.*?)\[/embed\]', lambda m: youtube_embed(m.group(1)) if 'youtu' in m.group(1) else '\n\n' + m.group(1).strip() + '\n\n', body, flags=re.I|re.S)
    body = re.sub(r'\[youtube\s+([^\]]+)\]', lambda m: youtube_embed(m.group(1)), body, flags=re.I)
    body = re.sub(r'\[youtube=([^\]&]+)[^\]]*\]', lambda m: youtube_embed(m.group(1)), body, flags=re.I)
    body = re.sub(r'(?m)^\s*(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s<]+)\s*$', lambda m: youtube_embed(m.group(1)), body)
    body = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', body)
    body = re.sub(r'([^\n])(!\[[^\]]*\]\([^\)]+\))', r'\1\n\n\2', body)
    body = re.sub(r'(\]\([^\)]+\))([^\n\s])', r'\1\n\n\2', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip()

def categories_tags(item):
    cats=[]; tags=[]
    for c in item.findall('category'):
        dom=c.get('domain') or ''
        val=(c.get('nicename') or c.text or '').strip()
        if not val: continue
        if dom=='category': cats.append(val)
        elif dom=='post_tag': tags.append(val)
    return sorted(set(cats)), sorted(set(tags))

attachment_by_id={}
attachment_refs=set()
for item in items:
    if gettext(item,'wp:post_type',ns) == 'attachment':
        pid=gettext(item,'wp:post_id',ns)
        url=gettext(item,'wp:attachment_url',ns) or gettext(item,'guid')
        if url and '/uploads/' in url:
            ref=resolve_upload_ref(url.split('/uploads/',1)[1])
            attachment_by_id[pid]=ref
            attachment_refs.add(ref)

# For the music site we keep the whole music uploads tree: it is small enough and preserves press-kit/audio assets.
needed=set(str(p.relative_to(UPLOADS)) for p in primary_upload_files)
needed |= attachment_refs
for item in items:
    typ=gettext(item,'wp:post_type',ns); status=gettext(item,'wp:status',ns)
    if status!='publish' or typ not in {'post','page'}: continue
    content=item.findtext('content:encoded', namespaces=ns) or ''
    needed |= refs_from_text(content)
    for meta in item.findall('wp:postmeta', namespaces=ns):
        if gettext(meta,'wp:meta_key',ns)=='_thumbnail_id':
            val=gettext(meta,'wp:meta_value',ns)
            if val in attachment_by_id: needed.add(attachment_by_id[val])

STATIC_UPLOADS.mkdir(parents=True, exist_ok=True)
copied=set(); missing=[]
for ref in sorted(needed):
    src=upload_source_by_rel.get(ref) or (UPLOADS / ref)
    if not src.exists():
        missing.append(ref); continue
    dst=STATIC_UPLOADS / ref
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or src.stat().st_size != dst.stat().st_size:
        shutil.copy2(src, dst)
    copied.add(ref)

# page mapping: import only stable useful music pages, skip sample/news/newsletter blanks.
page_map = {
    'https://www.danielebailo.it/music/': SITE / 'content/music/_index.md',
    'https://www.danielebailo.it/music/playlist/': SITE / 'content/music/songs.md',
    'https://www.danielebailo.it/music/about/': SITE / 'content/music/about.md',
    'https://www.danielebailo.it/music/chi-sono/': SITE / 'content/music/bio.md',
    'https://www.danielebailo.it/music/press-kit/': SITE / 'content/music/press-kit.md',
    'https://www.danielebailo.it/music/contatti/': SITE / 'content/music/contact.md',
}

imported_posts=[]; imported_pages=[]; skipped_pages=[]
for item in items:
    typ=gettext(item,'wp:post_type',ns); status=gettext(item,'wp:status',ns)
    if status!='publish' or typ not in {'post','page'}: continue
    title=gettext(item,'title') or 'Senza titolo'
    link=gettext(item,'link')
    date_raw=gettext(item,'wp:post_date',ns)
    date=date_raw[:10] if date_raw else ''
    content=item.findtext('content:encoded', namespaces=ns) or ''
    rewritten=rewrite_content(content)
    protected, embeds = protect_embeds(rewritten)
    body=cleanup_markdown(restore_embeds(md(protected, heading_style='ATX', bullets='-'), embeds))
    cats,tags=categories_tags(item)
    tags=sorted(set(tags + ['music']))
    fm={
        'title': title,
        'date': date,
        'draft': False,
        'categories': sorted(set(cats + ['music'])),
        'tags': tags,
        'original_url': link,
        'migration_source': 'wordpress-music'
    }
    for meta in item.findall('wp:postmeta', namespaces=ns):
        if gettext(meta,'wp:meta_key',ns)=='_thumbnail_id':
            val=gettext(meta,'wp:meta_value',ns)
            if val in attachment_by_id:
                fm['cover'] = local_upload_url(attachment_by_id[val])
                break
    if 'cover' not in fm:
        img_match=re.search(r'!\[[^\]]*\]\((/uploads/[^\)]+)\)', body)
        if img_match: fm['cover']=img_match.group(1)

    if typ=='post':
        slug=slugify(link or title)
        outdir=BLOG/slug
        # The music export is authoritative for music posts. Overwrite old imported duplicate if present.
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir/'.wp-imported').write_text('wordpress-music\n')
        (outdir/'index.md').write_text('---\n'+yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)+'---\n\n'+body+'\n', encoding='utf-8')
        imported_posts.append((title,str(outdir.relative_to(SITE)),link))
    else:
        dest=page_map.get(link)
        if not dest:
            skipped_pages.append((title,link)); continue
        page_fm={'title': title, 'description': '', 'original_url': link, 'migration_source': 'wordpress-music'}
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text('---\n'+yaml.safe_dump(page_fm, allow_unicode=True, sort_keys=False)+'---\n\n'+body+'\n', encoding='utf-8')
        imported_pages.append((title,str(dest.relative_to(SITE)),link))

media_size=sum((STATIC_UPLOADS/ref).stat().st_size for ref in copied if (STATIC_UPLOADS/ref).exists())
report=[]
report.append('# Music migration report\n')
report.append(f'- Imported published music posts into `/blog/`: {len(imported_posts)}')
report.append(f'- Imported stable music pages: {len(imported_pages)}')
report.append(f'- Skipped music pages: {len(skipped_pages)}')
report.append(f'- Copied selected music media files: {len(copied)}')
report.append(f'- Copied selected music media size: {media_size/1024/1024:.1f} MB')
report.append(f'- Missing selected music media: {len(missing)}')
report.append('\n## Imported posts\n')
for title,path,link in imported_posts: report.append(f'- `{path}` — {title} — {link}')
report.append('\n## Imported pages\n')
for title,path,link in imported_pages: report.append(f'- `{path}` — {title} — {link}')
if skipped_pages:
    report.append('\n## Skipped pages\n')
    for title,link in skipped_pages: report.append(f'- {title} — {link}')
if missing:
    report.append('\n## Missing media\n')
    for m in missing[:100]: report.append(f'- {m}')
REPORT.write_text('\n'.join(report)+'\n', encoding='utf-8')
print(REPORT)
print(f'imported_posts={len(imported_posts)} imported_pages={len(imported_pages)} copied_media={len(copied)} media_mb={media_size/1024/1024:.1f} missing={len(missing)}')
