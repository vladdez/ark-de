#!/usr/bin/env python3
"""Build the public static site from reviewed content only; no archive access."""
from pathlib import Path
from html import escape as e
import json
import shutil
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
CONFIG = json.loads((ROOT / 'site.json').read_text())
ARTICLES = json.loads((ROOT / 'content/articles.json').read_text())
SOURCES = {s['message_id']: s for s in json.loads((ROOT / 'content/sources.json').read_text())}
DATE = CONFIG['prepared']


def day(s):
    return '.'.join(reversed(s.split('-')))


def page(path, title, description, body, depth=0, kind='website'):
    prefix = '../' * depth
    canonical = urljoin(CONFIG['url'], path.replace('index.html', ''))
    full_title = title + ' · Ark DE'
    doc = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="{kind}"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="Ark DE"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(description)}">
<meta name="theme-color" content="#213c35"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head><body>
<a class="skip" href="#main">К содержанию</a><div class="wrap"><header class="header"><a class="brand" href="{prefix}index.html"><span class="brandmark" aria-hidden="true">a</span><span>Ark DE<small>Жизнь в Германии</small></span></a><nav aria-label="Основная навигация"><a href="{prefix}index.html#topics">Темы</a><a href="{prefix}sources/index.html">Источники</a><a href="{prefix}about/index.html">О базе</a></nav></header>
<main id="main">{body}</main><footer class="footer"><p>Ark DE · Независимая база знаний по обсуждениям эмиграции из России в Германию.<br>Не официальный сайт проекта «Ковчег».</p><a href="{prefix}about/index.html">Методика и границы базы ↗</a></footer></div></body></html>'''
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding='utf-8')


def refs(ids, prefix='../'):
    return ''.join(f'<a class="source-link" href="{prefix}sources/index.html#m{i}" aria-label="Источник: сообщение {i}">[{i}]</a>' for i in ids)


def article_ids(a):
    return sorted({i for o in a['observations'] for i in o['source_ids']})


def build():
    OUT.mkdir(exist_ok=True)
    (OUT/'assets').mkdir(exist_ok=True)
    for file in (ROOT/'assets').iterdir():
        shutil.copyfile(file, OUT/'assets'/file.name)
    cards = []
    for a in ARTICLES:
        search = ' '.join([a['title'], a['summary'], a['keywords'], a['takeaway'], *a['steps'], *[o['text'] for o in a['observations']]])
        cards.append(f'''<a class="card" href="{a['slug']}/index.html" data-category="{e(a['category'])}" data-search="{e(search)}"><span class="category">{e(a['category'])}</span><h3>{e(a['title'])}</h3><p>{e(a['summary'])}</p><span class="card-foot"><span>{len(article_ids(a))} сообщения · официальные ссылки</span><span class="arrow" aria-hidden="true">↗</span></span></a>''')
    filters = '<button type="button" data-filter="" aria-pressed="true">Все темы</button>' + ''.join(f'<button type="button" data-filter="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in dict.fromkeys(a['category'] for a in ARTICLES))
    body = f'''<section class="hero"><div><div class="eyebrow">Опыт сообщества · Русский → Германия</div><h1>Переезд в Германию.<br><em>Разберём по темам.</em></h1><p class="lead">Вопросы, опыт и полезные ориентиры из эмигрантского чата — с датами, источниками и ссылками на официальные правила.</p></div><aside class="hero-note"><div class="eyebrow">Как пользоваться</div><h2>Чужой опыт помогает<br>задать свой вопрос.</h2><p>Найдите тему, посмотрите контекст обсуждения и уточните действующие требования в официальном источнике.</p><a href="about/index.html#ask">Как задать вопрос ChatGPT ↗</a></aside></section>
<div class="stats"><div><strong>{len(ARTICLES)} материалов</strong>первая редакционная подборка</div><div><strong>{len(SOURCES)} сообщений</strong>использованы в статьях</div><div><strong>2022–2026</strong>период исходного архива</div></div>
<section class="catalogue" id="topics"><div class="section-heading"><div><div class="eyebrow">Библиотека</div><h2>С чего начнём?</h2></div><p id="result-count" role="status" aria-live="polite">Материалов: {len(ARTICLES)} из {len(ARTICLES)}</p></div>
<label for="search" class="sr-only">Поиск по опубликованным материалам</label><div class="searchbox"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="Например: ВНЖ, страховка, anabin" autocomplete="off"><button id="clear-search" type="button" hidden>Очистить</button></div><p class="note">Поиск по этим {len(ARTICLES)} материалам. Полный архив из 211 768 сообщений пока не опубликован.</p><div class="filters" aria-label="Фильтр по теме">{filters}</div><noscript><p class="note">Для поиска включите JavaScript. Все статьи доступны по ссылкам ниже.</p></noscript><div class="cards">{''.join(cards)}</div><div id="empty" class="empty" hidden><h3>Пока нет такого материала</h3><p>Попробуйте другое слово или сбросьте фильтр.</p><button class="copy" id="reset-filters" type="button">Сбросить поиск</button></div></section>
<section class="banner"><div><div class="eyebrow">Понятные источники</div><h2>Сохраняем контекст.<br>Не публикуем личную переписку.</h2></div><div><p>В статьях — редакторские пересказы отдельных сообщений без имён участников. Рядом указаны дата и номер источника. Полный архив проверен при импорте; это не означает, что все сообщения уже разобраны в статьях.</p><p><a href="about/index.html">Подробнее о методике →</a></p></div></section>'''
    page('index.html', 'Переезд и жизнь в Германии', 'Русскоязычная база знаний об эмиграции из России в Германию: 10 тем, датированные обсуждения и официальные источники.', body)
    (OUT/'markdown').mkdir(exist_ok=True)
    for a in ARTICLES:
        ids = article_ids(a)
        date_min, date_max = min(SOURCES[i]['date'] for i in ids), max(SOURCES[i]['date'] for i in ids)
        observations = ''.join(f'<p>{e(o["text"])} {refs(o["source_ids"])}</p>' for o in a['observations'])
        steps = ''.join(f'<li>{e(s)}</li>' for s in a['steps'])
        official = ''.join(f'<li><a href="{e(r["url"])}" rel="external">{e(r["label"])} ↗</a></li>' for r in a['official'])
        source_list = ''.join(f'<li><a href="../sources/index.html#m{i}">Сообщение {i}</a> · {day(SOURCES[i]["date"])}<br><span class="note">Редакторский пересказ</span></li>' for i in ids)
        body = f'''<p class="breadcrumbs"><a href="../index.html#topics">Все темы</a> / {e(a['category'])}</p><header class="article-head"><div class="eyebrow">{e(a['category'])}</div><h1>{e(a['title'])}</h1><p class="lead">{e(a['summary'])}</p><p class="meta">Подготовлено {day(DATE)} · Обсуждения: {day(date_min)} — {day(date_max)}</p></header>
<div class="layout"><article class="prose"><p class="note">Обзор отдельных обсуждений, а не заключение по вашему случаю. Условия и сроки сверяйте с компетентным ведомством.</p><h2 id="discussion">Что обсуждали в чате</h2>{observations}<h2 id="check">Что уточнить для своего случая</h2><ol>{steps}</ol><div class="callout"><h3>На что обратить внимание</h3><p>{e(a['takeaway'])}</p></div><h2 id="official">Где проверить требования</h2><ul class="resources">{official}</ul><p class="note">Официальные источники указаны отдельно от опыта участников. Наличие ссылки не подтверждает все высказывания в исходной переписке.</p><h2 id="sources">Основа статьи</h2><ul class="resources">{source_list}</ul></article>
<aside class="toc" aria-label="Содержание статьи"><strong>В этом материале</strong><a href="#discussion">Обсуждения</a><a href="#check">Что уточнить</a><a href="#official">Официальные источники</a><a href="#sources">Основа статьи</a><hr><a href="../markdown/{a['slug']}.md">Текст в Markdown ↗</a><p class="note">Для цитирования используйте адрес этой статьи и дату исходного сообщения.</p></aside></div>'''
        page(a['slug']+'/index.html', a['title'], a['summary'], body, depth=1, kind='article')
        md = [f'# {a["title"]}', '', a['summary'], '', f'Подготовлено: {DATE}. Обсуждения: {date_min} — {date_max}.', '', '## Что обсуждали в чате', '']
        for o in a['observations']:
            md += [o['text']+' '+ ' '.join(f'[Сообщение {i}]({CONFIG["url"]}sources/#m{i})' for i in o['source_ids']), '']
        md += ['## Что уточнить', '']+[f'{i}. {s}' for i,s in enumerate(a['steps'],1)]+['',a['takeaway'],'','## Официальные источники','']+[f'- [{r["label"]}]({r["url"]})' for r in a['official']]
        md += ['', 'Это обзор выбранных обсуждений, а не полный поиск по архиву или индивидуальное юридическое заключение.', '']
        (OUT/'markdown'/f'{a["slug"]}.md').write_text('\n'.join(md))
    source_cards=[]
    for mid,s in SOURCES.items():
        links=' · '.join(f'<a href="../{a["slug"]}/index.html">{e(a["title"])}</a>' for a in ARTICLES if mid in article_ids(a))
        source_cards.append(f'''<article class="source" id="m{mid}"><span class="badge">Редакторский пересказ</span><h2>Сообщение {mid}</h2><p class="meta">{day(s['date'])}</p><p>{e(s['summary'])}</p><p class="note">Использовано в материале:<br>{links}</p><details><summary>Ссылка на исходный архив</summary><p>Оригинал хранится в частном архиве: <code>{e(s['source_file'])}#{e(s['source_anchor'])}</code>. Имя автора и полный текст здесь не публикуются.</p><p>SHA-256 исходного текста: <code>{s['text_sha256']}</code></p></details></article>''')
    page('sources/index.html','Источники и контекст','Датированные редакторские пересказы сообщений, использованных в материалах Ark DE.',f'<p class="breadcrumbs"><a href="../index.html">Главная</a> / Источники</p><header class="article-head"><div class="eyebrow">Прозрачность</div><h1>Откуда взялись материалы</h1><p class="lead">{len(SOURCES)} сообщений из частного архива. Здесь опубликованы пересказы без имён, а не дословные цитаты или полный текст переписки.</p><p class="note">Номер и дата позволяют владельцу архива найти оригинал. Читатель публичного сайта видит только редакторское изложение.</p></header><div class="sources-grid">'+''.join(source_cards)+'</div>',depth=1)
    prompt=f'Прочитай подходящие статьи на {CONFIG["url"]} по вопросу: [мой вопрос]. Сошлись на страницы и даты обсуждений. Отдельно проверь действующие требования в официальных источниках. Если материала недостаточно или страница недоступна, скажи об этом. Не считай эту подборку полным архивом чата.'
    about=f'''<p class="breadcrumbs"><a href="../index.html">Главная</a> / О базе</p><header class="article-head"><div class="eyebrow">Методика</div><h1>Опыт людей.<br>Проверяемые ссылки.</h1><p class="lead">Ark DE помогает ориентироваться в вопросах переезда из России и жизни в Германии.</p></header><div class="layout"><article class="prose"><h2 id="scope">Что есть в этой версии</h2><p>Первая подборка: {len(ARTICLES)} материалов, основанных на {len(SOURCES)} выбранных сообщениях и проверке контекста их веток. Это не исчерпывающая обработка чата. Поиск на сайте работает только по опубликованным материалам.</p><h2 id="archive">Как проверен архив</h2><p>Исходный экспорт охватывает 13 апреля 2022 — 10 ноября 2026 года. Импортированы 211 768 обычных сообщений и 1 976 служебных записей из 212 HTML-страниц. При сопоставлении выполнено 4 037 196 проверок; расхождений не обнаружено.</p><p>В самом экспорте отсутствуют цели 9 868 ответов и 5 252 вложения; ещё 5 ответов относятся к другому чату. Успешный импорт не восстанавливает отсутствующие данные и не подтверждает фактическую верность сообщений.</p><h2 id="method">Как подготовлены статьи</h2><ol><li>Отобраны вопросы и сообщения, затем прочитаны связанные ответы там, где они доступны.</li><li>Подготовлены короткие пересказы без имён, контактов и личных подробностей.</li><li>Наблюдения из чата отделены от списка вопросов для проверки и официальных источников.</li><li>Сохранены дата, номер сообщения и контрольная сумма исходного текста для проверки владельцем архива.</li></ol><p>Даты подготовки статей не означают, что все нормы права проверены на эту дату. Условия зависят от процедуры и обстоятельств; для решений используйте актуальные сведения компетентного органа.</p><h2 id="privacy">Что опубликовано</h2><p>Сайт и его исходный код содержат только выбранные редакторские материалы. Полная переписка, имена участников и база данных не включены в публичный репозиторий.</p><h2 id="ask">Как задать вопрос ChatGPT</h2><p>Передайте адрес подходящей статьи вместе с вопросом. Пример запроса:</p><div class="prompt" id="prompt">{e(prompt)}</div><button class="copy" type="button" data-copy="#prompt">Скопировать запрос</button><p class="note">Доступ к сайту и полнота поиска зависят от используемого инструмента. Публикация не гарантирует индексацию всех страниц. <a href="https://developers.openai.com/api/docs/bots">Документация OpenAI о доступе к сайтам</a>.</p><h2 id="corrections">Исправления и развитие</h2><p>Материалы можно уточнять через <a href="{CONFIG['repository']}/issues">обсуждения ошибок в репозитории</a>. Не добавляйте в публичное обращение личные документы или чужую переписку. Следующие подборки должны расширять охват, сохраняя связь каждого утверждения с источником.</p></article><aside class="toc"><strong>О проекте</strong><a href="#scope">Охват</a><a href="#archive">Проверка архива</a><a href="#method">Методика</a><a href="#ask">Вопросы ChatGPT</a><a href="#corrections">Исправления</a></aside></div>'''
    page('about/index.html','О базе знаний','Охват, методика, ограничения и использование Ark DE для вопросов о жизни в Германии.',about,depth=1)
    page('404.html','Страница не найдена','Такой страницы нет в Ark DE.',f'<section class="hero"><div><div class="eyebrow">404</div><h1>Эта страница не найдена.</h1><p><a href="{CONFIG["url"]}">Перейти к темам →</a></p></div></section>')
    (OUT/'.nojekyll').write_text('')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+CONFIG['url']+'sitemap.xml\n')
    paths=['','sources/','about/']+[a['slug']+'/' for a in ARTICLES]
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(CONFIG["url"]+p)}</loc><lastmod>{DATE}</lastmod></url>' for p in paths)+'</urlset>')
    (OUT/'llms.txt').write_text('# Ark DE\n\nRussian-language editorial knowledge base about emigration from Russia to Germany. Initial selection: 10 articles based on 20 messages, NOT all 211,768 archived messages. Community observations are historical, not verified current law. Source pages contain anonymized paraphrases, not original transcripts.\n\n## Articles\n'+''.join(f'- [{a["title"]}]({CONFIG["url"]}{a["slug"]}/): {a["summary"]}\n' for a in ARTICLES)+'\n## Method and sources\n- '+CONFIG['url']+'about/\n- '+CONFIG['url']+'sources/\n')
    print(f'Built {len(ARTICLES)} articles and {len(SOURCES)} source summaries in {OUT}')


if __name__=='__main__':
    build()
