#!/usr/bin/env python3
"""Check source coverage, rendered links and per-article metadata before upload."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'


class Inspect(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids=set();self.links=[];self.meta={};self.titles=[];self.h1s=[]
        self.capture=None;self.text='';self.language=None
        self.feed(source)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate ID {a["id"]}'
            self.ids.add(a['id'])
        if tag=='html':self.language=a.get('lang')
        if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content')
        if tag in ('a','link','script'):
            ref=a.get('href',a.get('src'))
            if ref:self.links.append(ref)
        if tag in ('title','h1'):self.capture=tag;self.text=''
    def handle_endtag(self,tag):
        if tag==self.capture:
            (self.titles if tag=='title' else self.h1s).append(self.text)
            self.capture=None
    def handle_data(self,data):
        if self.capture:self.text+=data


def main():
    articles=json.loads((ROOT/'content/articles.json').read_text())
    sources=json.loads((ROOT/'content/sources.json').read_text())
    source_ids={s['message_id'] for s in sources}
    cited={i for a in articles for o in a['observations'] for i in o['source_ids']}
    assert cited==source_ids
    assert len(source_ids)==len(sources)==20
    assert len({a['slug'] for a in articles})==len(articles)==10
    allowed={'message_id','source_file','source_anchor','text_sha256','summary','date','type'}
    for s in sources:
        assert set(s)==allowed
        assert s['type']=='editorial_paraphrase'
        assert len(s['text_sha256'])==64
    pages={p.resolve():Inspect(p.read_text()) for p in DOCS.rglob('*.html')}
    count=0
    for p,info in pages.items():
        assert info.language=='ru',p
        assert len(info.h1s)==len(info.titles)==1,p
        for href in info.links:
            parts=urlsplit(href)
            if parts.scheme or parts.netloc:continue
            dest=(p.parent/unquote(parts.path)).resolve() if parts.path else p
            if dest.is_dir():dest=dest/'index.html'
            assert dest.is_relative_to(DOCS.resolve()),(p,href)
            assert dest.is_file(),(p,href)
            if parts.fragment and dest.suffix=='.html':assert unquote(parts.fragment) in pages[dest].ids,(p,href)
            count+=1
    for a in articles:
        info=pages[(DOCS/a['slug']/'index.html').resolve()]
        assert info.h1s==[a['title']]
        assert info.titles==[a['title']+' · Ark DE']
        for key in ('description','og:description','twitter:description'):assert info.meta[key]==a['summary']
        for key in ('og:title','twitter:title'):assert info.meta[key]==a['title']
        assert 'og:image' not in info.meta
    for file in ROOT.rglob('*'):
        if not file.is_file() or '__pycache__' in file.parts or '.git' in file.parts:continue
        assert file.suffix not in {'.sqlite','.db','.zip'},file
        assert not (file.name.startswith('messages') and file.suffix=='.html'),file
    result={'status':'PASS','html_pages':len(pages),'articles':len(articles),'source_summaries':len(sources),'local_links_checked':count,'article_metadata_checked':len(articles),'browser_visual_check':'Unavailable: no connected browser','scope':'Static structural checks; not a browser render or factual audit of the entire archive.'}
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
