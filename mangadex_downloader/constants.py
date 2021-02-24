import json

# Base url mangadex.org
BASE_URL = 'https://mangadex.org'

# Base url mangadex.org API for chapter
BASE_API_CHAPTER_URL = BASE_URL + '/api/v2/chapter/'

# Base url mangadex.org API for manga
BASE_API_MANGA_URL = BASE_URL + '/api/v2/manga/'

# Base url mangadex.org API for tag
BASE_API_TAG_URL = BASE_URL + '/api/v2/tag/'

class StringVar:
    """
    adapted from tkinter.StringVar()
    with set() and get() only
    """
    def __init__(self, initial_value: str=None):
        self._value = initial_value

    def set(self, value: str):
        self._value = value

    def get(self):
        return self._value

class MangaData:
    """
    a class representing manga info data
    """
    def __init__(self, data: dict):
        self._data = data
        self.chapters = self._parse_chapters(data['chapters'])
        self.language = data['language']
        self.title = data['title']
        self.description = data['description']
        self.artist = data['artist']
        self.author = data['author']
        self.genres = data['genres']
        self.cover = data['cover']
        self.status = data['status']

    def _parse_chapters(self, chapters):
        # MangaData will remove chapters, if same chapter.
        groups = {}
        for chap in chapters:
            if chap['chapter'] in groups.keys():
                continue
            else:    
                groups[chap['chapter']] = chap
        return [groups[i] for i in groups.keys()]
            
    def _get_total_chapters(self):
        if 'Oneshot' in self.genres:
            return 1
        else:
            return int(max([float(i['chapter']) for i in self.chapters]))

    def __repr__(self):
        return '<MangaData title="%s" chapters=%s language=%s>' %(
            self.title,
            self._get_total_chapters(),
            self.language
        )

    def to_json(self):
        return json.dumps(self._data)
    
    def to_dict(self):
        return self._data


class MangaChapterData:
    """
    a class representing manga chapter info data
    """
    def __init__(self, data: dict):
        self._data = data
        self.title = data['title']
        self.chapter = data['chapter']
        self.volume = data['volume']
        self.page = data['page']
        self.id = data['chapter-id']
        self.primary_url = data['primary_url']
        self.secondary_url = data['secondary_url']

    def __repr__(self):
        return '<MangaChapterData page=%s title=%s chapter=%s volume=%s>' % (
            self.page,
            self.title,
            self.chapter,
            self.volume
        )

    def to_json(self):
        return json.dumps(self._data)

    def to_dict(self):
        return self._data
