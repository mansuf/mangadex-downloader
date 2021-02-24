import re
import json
import html
from bs4 import BeautifulSoup
from mangadex_downloader.constants import (
    BASE_URL,
    MangaChapterData,
    StringVar
)

def decode_description(desc):
    # decode bbcode into string
    REPLACERS = {
        '[b]': '',
        '[i]': '',
        '[b]-[i]': '',
        '[/b]': '',
        '[/i]': '',
        '[*]': '',
        '[/url]': ''
    }
    strings = StringVar()
    for replacer in REPLACERS.keys():
        if strings.get() is None:
            strings.set(desc.replace(replacer, REPLACERS[replacer]))
        else:
            strings.set(strings.get().replace(replacer, REPLACERS[replacer]))
    result = html.unescape(strings.get())
    return result

def parse_infos(body_string, lang='English'):
    """
    parse manga info, return :class:`MangaData`
    """
    bs = BeautifulSoup(body_string, 'html.parser')
    chapters = bs.find_all(class_=re.compile('chapter-row d-flex row no-gutters'))
    info = {}
    chapters_ = []
    for i in chapters:
        inf = {}
        language = None
        # finding language
        for l in i.find_all('span'):
            try:
                l.attrs['title']
            except KeyError:
                continue
            else:
                if 'rounded' in l.attrs['class']:
                    language = l.attrs['title']
                else:
                    continue
        if language is None:
            continue
        # check if language is same or not
        if lang.lower() != language.lower():
            continue
        else:
            inf['language'] = language
        # finding url chapter
        for a in i.find_all('a'):
            try:
                a.attrs['class']
            except KeyError:
                continue
            else:
                if 'text-truncate' in a.attrs['class']:
                    inf['url'] = BASE_URL + a.attrs['href']
                else:
                    continue
        # finding group
        for a in i.find_all('a'):
            try:
                a.attrs['href']
            except KeyError:
                continue
            else:
                if '/group/' in a.attrs['href']:
                    inf['group'] = a.decode_contents()
                else:
                    continue
        # finding uploader, chapter, volume
        try:
            i.attrs['data-id']
        except KeyError:
            continue
        else:
            inf['uploader'] = i.attrs['data-uploader']
            inf['chapter'] = i.attrs['data-chapter']
            inf['volume'] = i.attrs['data-volume']
            inf['chapter-id'] = i.attrs['data-id']
            info['manga-id'] = i.attrs['data-manga-id']
            chapters_.append(inf)
    # finding title
    t = bs.find_all('span')
    info['chapters'] = chapters_
    for i in t:
        try:
            i.attrs['class']
        except KeyError:
            continue
        else:
            if 'mx-1' in i.attrs['class']:
                info['title'] = i.decode_contents()
            else:
                continue
    return info

def parse_chapters_info(json_data: str):
    """
    parse manga chapter info, return :class:`MangaChapterData`
    """
    data = json.loads(json_data)['data']
    infos = []
    num = 1
    for i in data['pages']:
        info = {}
        info['title'] = data['mangaTitle']
        info['chapter'] = data['chapter']
        info['chapter-id'] = data['id']
        info['volume'] = data['volume']
        info['page'] = num
        info['primary_url'] = data['server'] + data['hash'] + '/' +  i
        try:
            info['secondary_url'] = data['serverFallback'] + data['hash'] + '/' + i
        except KeyError:
            info['secondary_url'] = None
        infos.append(info)
        num += 1
    return [MangaChapterData(i) for i in infos]

def get_absolute_url(body_string: str):
    """Get absolute manga mangadex url"""
    parser = BeautifulSoup(body_string, 'html.parser')
    for link_elements in parser.find_all('link'):
        # aiming for canonical link
        try:
            rel = link_elements.attrs['rel']
            href = link_elements.attrs['href']
        except KeyError:
            continue
        else:
            if 'canonical' in rel:
                return href
            else:
                continue

