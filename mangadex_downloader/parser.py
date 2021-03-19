import re
import json
import html
from bs4 import BeautifulSoup
from mangadex_downloader.constants import (
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

def get_manga_id(body_string: str):
    """Finding manga id with scrapping"""
    parser = BeautifulSoup(body_string, 'html.parser')
    # finding data-manga-id in every buttons element
    for button in parser.find_all('button'):
        if button.attrs.get('data-manga-id') is None:
            continue
        else:
            return button.attrs.get('data-manga-id')
    # finding data-title-id in every buttons element
    for button in parser.find_all('button'):
        if button.attrs.get('data-title-id'):
            if button.attrs.get('data-title-id') is None:
                continue
            else:
                return button.attrs.get('data-title-id')