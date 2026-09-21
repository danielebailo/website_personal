from pathlib import Path
from lxml import etree as ET
from markdownify import markdownify as md
import yaml, re, html, shutil, urllib.parse
from datetime import datetime

XML = Path('/Users/danielebailo/.pi/tmp/wordpress-export/wordpress-personale-export.xml')
UPLOADS = Path('/Users/danielebailo/.pi/tmp/wordpress-export/uploads')
SITE = Path('/Users/danielebailo/Documents/PROJ.SRC/github/website_personal')
BLOG = SITE / 'content' / 'blog'
STATIC_UPLOADS = SITE / 'static' / 'uploads'
REPORT = SITE / 'MIGRATION_REPORT.md'

ns = {
    'wp':'http://wordpress.org/export/1.2/',
    'content':'http://purl.org/rss/1.0/modules/content/',
    'excerpt':'http://wordpress.org/export/1.2/excerpt/',
    'dc':'http://purl.org/dc/elements/1.1/'
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
    replacements = str.maketrans({'à':'a','è':'e','é':'e','ì':'i','ò':'o','ù':'u','ç':'c'})
    value = value.translate(replacements)
    value = re.sub(r'[^a-z0-9]+', '-', value).strip('-')
    return value or 'post'

def categories_tags(item):
    cats=[]; tags=[]
    for c in item.findall('category'):
        dom=c.get('domain') or ''
        val=(c.get('nicename') or c.text or '').strip()
        if not val: continue
        if dom=='category': cats.append(val)
        elif dom=='post_tag': tags.append(val)
    return sorted(set(cats)), sorted(set(tags))

def normalize_upload_ref(ref):
    ref = html.unescape(ref).split('?')[0].rstrip('.,;')
    ref = urllib.parse.unquote(ref)
    return ref.lstrip('/')

def refs_from_text(text):
    refs=set()
    patterns = [
        r'https?://(?:www\.)?danielebailo\.it/(?:music/)?wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://localhost/wordpress3/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://danielebailo\.files\.wordpress\.com/([^\s"\'<>\)]+)',
        r'https?://glistancocchi\.files\.wordpress\.com/([^\s"\'<>\)]+)',
    ]
    for pattern in patterns:
        for u in re.findall(pattern, text or ''):
            refs.add(normalize_upload_ref(u))
    return refs

# attachment id -> upload path
attachment_by_id={}
attachment_refs=set()
for item in items:
    if gettext(item,'wp:post_type',ns) == 'attachment':
        pid=gettext(item,'wp:post_id',ns)
        url=gettext(item,'wp:attachment_url',ns) or gettext(item,'guid')
        if url and '/wp-content/uploads/' in url:
            ref=normalize_upload_ref(url.split('/wp-content/uploads/',1)[1])
            attachment_by_id[pid]=ref
            attachment_refs.add(ref)

# collect post refs + featured media
post_count=0; page_count=0; copied=set(); missing=[]; imported=[]
all_needed=set(attachment_refs)
for item in items:
    typ=gettext(item,'wp:post_type',ns); status=gettext(item,'wp:status',ns)
    if status!='publish' or typ not in {'post','page'}: continue
    content=item.findtext('content:encoded', namespaces=ns) or ''
    all_needed |= refs_from_text(content)
    for meta in item.findall('wp:postmeta', namespaces=ns):
        key=gettext(meta,'wp:meta_key',ns)
        val=gettext(meta,'wp:meta_value',ns)
        if key == '_thumbnail_id' and val in attachment_by_id:
            all_needed.add(attachment_by_id[val])

# copy selected media
STATIC_UPLOADS.mkdir(parents=True, exist_ok=True)
for ref in sorted(all_needed):
    src=UPLOADS / ref
    if not src.exists():
        missing.append(ref); continue
    dst=STATIC_UPLOADS / ref
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or src.stat().st_size != dst.stat().st_size:
        shutil.copy2(src, dst)
    copied.add(ref)

# replace wp upload URLs, WordPress shortcodes and embeds with Hugo-friendly Markdown/HTML
all_upload_files = [p for p in UPLOADS.rglob('*') if p.is_file()]
upload_by_name = {}
for p in all_upload_files:
    upload_by_name.setdefault(p.name.lower(), str(p.relative_to(UPLOADS)))

def resolve_upload_ref(ref):
    ref = normalize_upload_ref(ref)
    if (UPLOADS / ref).exists():
        return ref
    name = Path(ref).name.lower()
    return upload_by_name.get(name, ref)

def local_upload_url(ref):
    return '/uploads/' + resolve_upload_ref(ref).replace(' ', '%20')

def protect_embeds(content):
    embeds = []
    def repl(m):
        raw = m.group(0)
        raw = re.sub(r'\s+', ' ', raw).strip()
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
    patterns = [
        r'youtube\.com/embed/([A-Za-z0-9_-]+)',
        r'youtube\.com/watch\?v=([A-Za-z0-9_-]+)',
        r'youtu\.be/([A-Za-z0-9_-]+)',
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            video_id = m.group(1)
            break
    if not video_id:
        return url
    return f'\n\n<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{video_id}" title="YouTube video" loading="lazy" allowfullscreen></iframe></div>\n\n'

def rewrite_content(content):
    content = content or ''
    patterns = [
        r'https?://(?:www\.)?danielebailo\.it/(?:music/)?wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://localhost/wordpress3/wp-content/uploads/([^\s"\'<>\)]+)',
        r'https?://danielebailo\.files\.wordpress\.com/([^\s"\'<>\)]+)',
        r'https?://glistancocchi\.files\.wordpress\.com/([^\s"\'<>\)]+)',
    ]
    for pattern in patterns:
        content = re.sub(pattern, lambda m: local_upload_url(m.group(1)), content)

    content = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', r'\n\n\1\n\n', content, flags=re.I|re.S)
    return content

def convert_youtube_markdown(body):
    body = re.sub(r'\[embed[^\]]*\](.*?)\[/embed\]', lambda m: youtube_embed(m.group(1)) if 'youtu' in m.group(1) else '\n\n' + m.group(1).strip() + '\n\n', body, flags=re.I|re.S)
    body = re.sub(r'\[youtube\s+([^\]]+)\]', lambda m: youtube_embed(m.group(1)), body, flags=re.I)
    body = re.sub(r'\[youtube=([^\]&]+)[^\]]*\]', lambda m: youtube_embed(m.group(1)), body, flags=re.I)
    body = re.sub(r'(?m)^\s*(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s<]+)\s*$', lambda m: youtube_embed(m.group(1)), body)
    return body

def cleanup_markdown(body):
    body = body.replace('\xa0', ' ')
    body = convert_youtube_markdown(body)
    body = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', body)
    body = re.sub(r'([^\n])(!\[[^\]]*\]\([^\)]+\))', r'\1\n\n\2', body)
    body = re.sub(r'(\]\([^\)]+\))([^\n\s])', r'\1\n\n\2', body)
    body = re.sub(r'\*\[([^\]]+)\]\(([^\)]+)\)\n\n\*', r'*[\1](\2)*\n\n', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip()

# clear previous imported marker posts, keep test? remove only wp-imported dirs
for child in BLOG.iterdir() if BLOG.exists() else []:
    marker=child / '.wp-imported'
    if child.is_dir() and marker.exists():
        shutil.rmtree(child)

for item in items:
    typ=gettext(item,'wp:post_type',ns); status=gettext(item,'wp:status',ns)
    if status!='publish' or typ not in {'post','page'}: continue
    if typ=='page':
        page_count += 1
        # don't import WordPress structural pages into blog; report only for now
        continue
    post_count += 1
    title=gettext(item,'title') or 'Senza titolo'
    link=gettext(item,'link')
    slug=slugify(link or title)
    date_raw=gettext(item,'wp:post_date',ns)
    date=(date_raw[:10] if date_raw else '')
    cats,tags=categories_tags(item)
    content=item.findtext('content:encoded', namespaces=ns) or ''
    excerpt=item.findtext('excerpt:encoded', namespaces=ns) or ''
    # add canonical music tag when old categories indicate music
    music_markers={'musica','musica-video','music','exfalsoquodlibet','jazz','guitar','song','original-song','album','chitarra-acustica'}
    if music_markers.intersection(set(cats+tags)) and 'music' not in tags:
        tags.append('music')
    fm={
        'title': title,
        'date': date,
        'draft': False,
        'categories': cats,
        'tags': sorted(set(tags)),
        'original_url': link,
        'migration_source': 'wordpress-personale'
    }
    # featured image if present
    for meta in item.findall('wp:postmeta', namespaces=ns):
        key=gettext(meta,'wp:meta_key',ns); val=gettext(meta,'wp:meta_value',ns)
        if key=='_thumbnail_id' and val in attachment_by_id:
            fm['cover'] = '/uploads/' + attachment_by_id[val].replace(' ', '%20')
            break
    rewritten=rewrite_content(content)
    protected, embeds = protect_embeds(rewritten)
    body=cleanup_markdown(restore_embeds(md(protected, heading_style='ATX', bullets='-'), embeds))
    if excerpt.strip():
        fm['summary']=md(excerpt, heading_style='ATX').strip()
    outdir=BLOG/slug
    # avoid collision
    if outdir.exists() and not (outdir/'.wp-imported').exists():
        outdir=BLOG/(slug+'-wp')
    n=2
    base=outdir
    while outdir.exists():
        if (outdir/'.wp-imported').exists(): break
        outdir=Path(str(base)+f'-{n}'); n+=1
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir/'.wp-imported').write_text('wordpress-personale\n')
    (outdir/'index.md').write_text('---\n'+yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)+'---\n\n'+body+'\n', encoding='utf-8')
    imported.append((title, str(outdir.relative_to(SITE)), link))

media_size=sum((STATIC_UPLOADS/ref).stat().st_size for ref in copied if (STATIC_UPLOADS/ref).exists())
report=[]
report.append('# Migration report\n')
report.append(f'- Imported published posts into `/blog/`: {post_count}')
report.append(f'- WordPress published pages not auto-imported: {page_count}')
report.append(f'- Copied selected media files: {len(copied)}')
report.append(f'- Copied selected media size: {media_size/1024/1024:.1f} MB')
report.append(f'- Missing selected media: {len(missing)}')
report.append('\n## Imported posts sample\n')
for title,path,link in imported[:40]:
    report.append(f'- `{path}` — {title} — {link}')
if missing:
    report.append('\n## Missing media\n')
    for m in missing[:100]: report.append(f'- {m}')
REPORT.write_text('\n'.join(report)+'\n', encoding='utf-8')
print(REPORT)
print(f'imported_posts={post_count} copied_media={len(copied)} media_mb={media_size/1024/1024:.1f} missing={len(missing)}')
