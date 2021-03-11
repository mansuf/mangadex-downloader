import requests
import json
from mangadex_downloader.parser import (
    parse_chapters_info,
    decode_description,
    get_absolute_url,
    get_manga_id
)
from mangadex_downloader.constants import (
    get_manga_chapter_url,
    get_manga_api_url,
    BASE_API_TAG_URL,
    BASE_API_USER_URL,
    BASE_API_GROUP_URL,
    MangaData
)
from .errors import (
    FetcherError,
    MangaNotFound,
    UserBanned
)

class MangadexFetcher:
    """
    a class representing fetcher for mangadex
    """
    def __init__(self, url: str, verbose=False):
        self.url = url
        self._verbose = verbose

    def _log_info(self, message: str):
        if self._verbose:
            print('[INFO] [FETCHER] %s' % (message))
        else:
            return

    def _log_error(self, message: str):
        if self._verbose:
            print('[ERROR] [FETCHER] %s' % (message))
        else:
            return

    def _get_api_tag(self, tag):
        r = requests.get(BASE_API_TAG_URL + str(tag))
        if r.status_code != 200:
            raise FetcherError('mangadex send %s code' % (r.status_code))
        data = json.loads(r.text)
        return data['data']['name']

    def _get_artist_or_author(self, artists):
        artist = ''
        if len(artists) == 1:
            return artists[0]
        elif len(artists) > 1:
            for a in artists:
                artist += a
        return artist

    def get(self, fetch_chapters=True):
        manga = {}
        chapters = []
        # UPDATE: MangadexFetcher now always using API
        # for fetching all information manga
        # because scrapping can't get enough information manga
        self._log_info('Requesting info to mangadex main website')
        r = requests.get(self.url)

        self._log_info('Checking if ip user are banned or not')
        # Raise error if we're banned from mangadex
        if 'Too many hits detected from ' in r.text:
            self._log_error('Your ip is banned from mangadex')
            raise UserBanned('Your ip is banned from mangadex')

        self._log_info('Checking if given url manga is exist or not')
        # Raise error if given manga not exist
        if '<strong>Warning:</strong> Manga' in r.text:
            self._log_error('Manga not exist')
            raise MangaNotFound('manga not exist')
        manga_id = get_manga_id(r.text)
        absolute_url = get_absolute_url(r.text)
        
        # Begin the fetching !!
        self._log_info('Retrieving info from mangadex API')
        r = requests.get(get_manga_api_url(manga_id))
        if r.status_code != 200:
            self._log_error('Mangadex send %s code' % (r.status_code))
            raise FetcherError('mangadex send %s code' % (r.status_code))

        data = json.loads(r.text)['data']

        self._log_info('Parsing manga')
        # Parse manga
        manga['title'] = data['manga']['title']
        manga['url'] = absolute_url
        manga['description'] = decode_description(data['manga']['description'])
        manga['artist'] = self._get_artist_or_author(data['manga']['artist'])
        manga['author'] = self._get_artist_or_author(data['manga']['author'])
        manga['genres'] = [self._get_api_tag(i) for i in data['manga']['tags']]
        manga['cover'] = data['manga']['mainCover']
        manga['language'] = data['manga']['publication']['language']
        manga['status'] = data['manga']['publication']['status']

        # Counting total chapters in Global language
        total_chapters = []
        for chap in data['chapters']:
            # skip parsing chapter, if selected chapter is not global language
            if chap['language'] != 'gb':
                continue
            else:
                total_chapters.append(chap)
        manga['total_chapters'] = len(total_chapters)
        manga['chapters'] = None
        if not fetch_chapters:
            return MangaData(manga)

        # for store user cache to speed up process
        user_cache = {}

        self._log_info('Fetch and Parsing Chapters')
        # Parse Chapters
        for chap in total_chapters:
            chapter = {}
            chapter['id'] = chap['id']
            chapter['chapter'] = chap['chapter']
            chapter['volume'] = chap['volume']
            groups = []

            # Parsing groups
            for grp in chap['groups']:
                for grps in data['groups']:
                    if grp == grps['id']:
                        groups.append(grps['name'])
            chapter['groups'] = groups

            # Parsing user / uploader
            # we're using cache to speed up process
            try:
                chapter['uploader'] = user_cache[chap['uploader']]
            except KeyError:
                user = json.loads(requests.get(BASE_API_USER_URL + str(chap['uploader'])).text)['data']['username']
                user_cache[chap['uploader']] = user
                chapter['uploader'] = user

            chapters.append(chapter)
        
        manga['chapters'] = chapters
        return MangaData(manga)


class MangadexChapterFetcher:
    """
    a class representing fetcher for mangadex chapter
    """
    def __init__(self, chapter_id: str, data_saver=False):
        if isinstance(chapter_id, str):
            self.chapter_id = chapter_id
        else:
            self.chapter_id = str(chapter_id)
        self._data_saver = data_saver

    def get(self):
        r = requests.get(get_manga_chapter_url(self.chapter_id, self._data_saver))
        return parse_chapters_info(r.text)