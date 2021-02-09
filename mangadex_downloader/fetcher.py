import requests
import json
from mangadex_downloader.parser import (
    parse_infos,
    parse_chapters_info,
    decode_description
)
from mangadex_downloader.constants import (
    BASE_API_CHAPTER_URL,
    BASE_API_MANGA_URL,
    BASE_API_TAG_URL,
    MangaData
)

class MangadexFetcher:
    """
    a class representing fetcher for mangadex
    """
    def __init__(self, url: str, language='English'):
        self.url = url
        self.lang = language

    def _get_url(self):
        url = self.url
        if '/chapters/' in url:
            return self.url
        elif '/chapters' in url:
            return self.url + '/'
        elif '/chapters' not in url:
            return self.url + '/chapters/'

    def _get_api_tag(self, tag):
        data = json.loads(requests.get(BASE_API_TAG_URL + str(tag)).text)
        return data['data']['name']

    def _get_artist_or_author(self, artists):
        artist = ''
        if len(artists) == 1:
            return artists[0]
        elif len(artists) > 1:
            for a in artists:
                artist += a
        return artist

    def _get_api_manga(self, result, manga_id):
        data = json.loads(requests.get(BASE_API_MANGA_URL + manga_id).text)['data']
        result['title'] = data['title']
        result['description'] = decode_description(data['description'])
        result['artist'] = self._get_artist_or_author(data['artist'])
        result['author'] = self._get_artist_or_author(data['author'])
        result['genres'] = [self._get_api_tag(i) for i in data['tags']]
        result['cover'] = data['mainCover']
        result['language'] = data['publication']['language']
        result['status'] = data['publication']['status']

    def get(self):
        num = 1
        results = []
        while True:
            print(self._get_url() + str(num))
            r = requests.get(self._get_url() + str(num))
            if 'Too many hits detected from ' in r.text:
                raise Exception('Your ip is banned from mangadex')
            if '<strong>Warning:</strong> No results found.' in r.text:
                break
            i = parse_infos(r.text)
            for a in i['chapters']:
                results.append(a)
            # for those manga who dont have chapters more than 100
            if 'page-item' not in r.text:
                break
            else:
                num += 1
        i['chapters'] = results
        # Web scrapping cannot extract description, genres, etc.
        # we're using mangadex API for getting description, genres, etc.
        self._get_api_manga(i, i['manga-id'])
        return MangaData(i)

class MangadexChapterFetcher:
    """
    a class representing fetcher for mangadex chapter
    """
    def __init__(self, chapter_id: str):
        self.chapter_id = chapter_id

    def get(self):
        r = requests.get(BASE_API_CHAPTER_URL + self.chapter_id)
        return parse_chapters_info(r.text)