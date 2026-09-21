from pathlib import Path
import re, urllib.parse, urllib.request

SITE=Path('/Users/danielebailo/Documents/PROJ.SRC/github/website_personal')
STATIC=SITE/'static/uploads'
content_paths=list((SITE/'content/blog').glob('*/index.md'))+list((SITE/'content/music').glob('*.md'))

# Known broken legacy media references: fix to available local assets or remove dead external media links.
known_replacements = {
    'https://www.danielebailo.it/job/wp-content/uploads/2023/11/Schermata-2023-11-22-alle-14.42.55-e1700660675319.png': '/uploads/2023/12/Schermata-2023-11-22-alle-14.42.55-e1700660675319-scaled.webp',
    '/uploads/2023/11/Schermata-2023-11-22-alle-14.42.55-e1700660675319.png': '/uploads/2023/12/Schermata-2023-11-22-alle-14.42.55-e1700660675319-scaled.webp',
    'https://www.danielebailo.it/job/wp-content/uploads/2023/12/Schermata-2023-11-22-alle-14.42.55-e1700660675319-scaled.webp': '/uploads/2023/12/Schermata-2023-11-22-alle-14.42.55-e1700660675319-scaled.webp',
    '![](http://exfalsoquodlibet.org/wp-content/uploads/wppa/43.jpg)': '![](/uploads/2013/04/soundcheck-3.jpg)',
    '![](http://exfalsoquodlibet.org/wp-content/uploads/2013/04/soundcheck-3.jpg)': '![](/uploads/2013/04/soundcheck-3.jpg)', 
    '[zaino da inter-railer](http://blogstelsclub.com/wp-content/uploads/2011/09/huge-backpack.jpg)\n\n': 'zaino da inter-railer',
    '[link diretto all\'mp3](http://exfalsoquodlibet.org/wp-content/uploads/music/Soundcheck_candidate.mp3)': 'video YouTube qui sotto',
}
for p in content_paths:
    s=p.read_text(errors='ignore')
    ns=s
    # Repair accidental partial replacements from older script runs.
    ns=ns.replace('http://blogstelsclub.com/wp-contenthttp://blogstelsclub.com/wp-content/uploads/2011/09/huge-backpack.jpg', 'http://blogstelsclub.com/wp-content/uploads/2011/09/huge-backpack.jpg')
    ns=ns.replace('http://exfalsoquodlibet.org/wp-contenthttp://exfalsoquodlibet.org/wp-content/uploads/music/Soundcheck_candidate.mp3', 'http://exfalsoquodlibet.org/wp-content/uploads/music/Soundcheck_candidate.mp3')
    for old,new in known_replacements.items():
        ns=ns.replace(old,new)
    if ns!=s:
        p.write_text(ns)

refs=[]
for p in content_paths:
    s=p.read_text(errors='ignore')
    for u in re.findall(r'/uploads/[^\s\)"<>]+', s):
        rel=urllib.parse.unquote(u.split('/uploads/',1)[1]).split('?',1)[0]
        if not (STATIC/rel).exists(): refs.append(rel)
refs=sorted(set(refs))
print('missing refs in content:', len(refs))

downloaded=[]; failed=[]
for rel in refs:
    dst=STATIC/rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    quoted=urllib.parse.quote(rel, safe='/._-')
    candidates=[
        'https://www.danielebailo.it/music/wp-content/uploads/'+quoted,
        'https://www.danielebailo.it/wp-content/uploads/'+quoted,
        'https://i0.wp.com/www.danielebailo.it/music/wp-content/uploads/'+quoted,
        'https://i1.wp.com/www.danielebailo.it/music/wp-content/uploads/'+quoted,
        'https://i2.wp.com/www.danielebailo.it/music/wp-content/uploads/'+quoted,
    ]
    ok=False
    for url in candidates:
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status != 200: continue
                data=r.read()
                if len(data) < 64: continue
                dst.write_bytes(data)
                downloaded.append((rel,url,len(data)))
                ok=True
                break
        except Exception:
            pass
    if not ok:
        failed.append(rel)
print('downloaded:', len(downloaded))
print('failed:', len(failed))
for rel,url,size in downloaded[:30]: print('OK', rel, size, url)
if failed:
    print('\nFAILED')
    for rel in failed[:100]: print(rel)
