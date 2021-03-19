import json

# Base url API mangadex.org
BASE_API_URL = 'https://api.mangadex.org/v2'

# Base url mangadex.org API for chapter
def get_manga_chapter_url(chapter_id, data_saver=False):
    if data_saver:
        return BASE_API_URL + '/chapter/' + chapter_id + '?saver=true'
    else:
        return BASE_API_URL + '/chapter/' + chapter_id

# Base url mangadex.org API for manga
def get_manga_api_url(manga_id, include_chapters=True):
    if include_chapters:
        return BASE_API_URL + '/manga/' + manga_id + '?include=chapters'
    else:
        return BASE_API_URL + '/manga/' + manga_id

# Base url mangadex.org API for tag
BASE_API_TAG_URL = BASE_API_URL + '/tag/'

# Base url mangadex.org API for group
BASE_API_GROUP_URL = BASE_API_URL + '/group/'

# Base url mangadex.org API for user
BASE_API_USER_URL = BASE_API_URL + '/user/'

class StringVar:
    """
    adapted from tkinter.StringVar()
    with set() and get() only
    """
    def __init__(self, initial_value: str=None):
        self._value = initial_value or ''

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
        self.title = filter_forbidden_names(data['title'])
        self.description = data['description']
        self.artist = data['artist']
        self.author = data['author']
        self.genres = data['genres']
        self.cover = data['cover']
        self.status = data['status']
        self.total_chapters = data['total_chapters']
        self.latest_chapters = self._get_latest_chapters()

    def _parse_chapters(self, chapters):
        if chapters is None:
            return
        # MangaData will remove chapters, if same chapter.
        groups = {}
        for chap in chapters:
            if chap['chapter'] in groups.keys():
                continue
            else:    
                groups[chap['chapter']] = chap
        return [groups[i] for i in groups.keys()]
            
    def _get_latest_chapters(self):
        if 'Oneshot' in self.genres:
            return 1
        else:
            return int(max([float(i['chapter']) for i in self.chapters]))

    def _get_total_chapters(self):
        if 'Oneshot' in self.genres:
            return 1
        elif self.chapters is None:
            return self.total_chapters
        else:
            return len(self.chapters)

    def __repr__(self):
        return '<MangaData title="%s" total_chapters=%s language=%s>' %(
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
        self.title = filter_forbidden_names(data['title'])
        self.chapter = data['chapter']
        self.volume = data['volume']
        self.page = data['page']
        self.id = data['chapter-id']
        self.primary_url = data['primary_url']
        self.secondary_url = data['secondary_url']

    def __repr__(self):
        return '<MangaChapterData page=%s title="%s" chapter=%s volume=%s>' % (
            self.page,
            self.title,
            self.chapter,
            self.volume
        )

    def to_json(self):
        return json.dumps(self._data)

    def to_dict(self):
        return self._data

def filter_forbidden_names(string: str):
    """Filter symbol names to prevent error when creating folder or file"""
    result = ''
    UNIX_FORBIDDEN_NAMES = ['/']
    MAC_OS_FORBIDDEN_NAMES = [':']
    WINDOWS_FORBIDDEN_NAMES = ['<', '>', ':', '\"', '/', '\\', '|', '?', '*']
    for word in string:
        if word in UNIX_FORBIDDEN_NAMES:
            continue
        elif word in MAC_OS_FORBIDDEN_NAMES:
            continue
        elif word in WINDOWS_FORBIDDEN_NAMES:
            continue
        else:
            result += word
    final = StringVar(result)
    # remove dot or space in ends words
    # to prevent error when writing file or folder in windows
    while True:
        if final.get()[len(final.get()) - 1] == '.' or final.get()[len(final.get()) - 1] == ' ':
            r = final.get()[0:len(final.get()) - 1]
            final.set(r)
        else:
            break
    return final.get()
