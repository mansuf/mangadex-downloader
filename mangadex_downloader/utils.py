import re
import time
import signal
import json
import logging
import sys
from pathvalidate import sanitize_filename
from enum import Enum
from .errors import InvalidURL, NotLoggedIn
from .downloader import FileDownloader, _cleanup_jobs
from .network import Net

log = logging.getLogger(__name__)

valid_cover_types = [
    'original',
    '512px',
    '256px',
    'none'
]

default_cover_type = "original"

# Compliance with Tachiyomi local JSON format
class MangaStatus(Enum):
    Ongoing = "1"
    Completed = "2"
    Hiatus = "6"
    Cancelled = "5"

def validate_url(url):
    """Validate mangadex url and return the uuid"""
    re_url = re.compile(r'([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})')
    match = re_url.search(url)
    if match is None:
        raise InvalidURL('Invalid MangaDex URL or manga id')
    return match.group(1)

def download(url, file, progress_bar=True, replace=False, **headers):
    """Shortcut for :class:`FileDownloader`"""
    downloader = FileDownloader(
        url,
        file,
        progress_bar,
        replace,
        **headers
    )
    downloader.download()
    downloader.cleanup()

def write_details(manga, path):
    data = {}
    data['title'] = manga.title

    # Parse authors
    authors = ""
    for index in range(len(manga.authors)):
        author = manga.authors[index]
        if index < (len(manga.authors) - 1):
            authors += author + ", "
        # If this is last index, append author without comma
        else:
            authors += author
    data['author'] = authors

    # Parse artists
    artists = ""
    for index in range(len(manga.artists)):
        artist = manga.artists[index]
        if index < (len(manga.artists) - 1):
            artists += artist + ", "
        # If this is last index, append artist without comma
        else:
            artists += artist
    data['artist'] = artists

    data['description'] = manga.description
    data['genre'] = manga.genres
    data['status'] = MangaStatus[manga.status].value
    data['_status values'] = [
        "0 = Unknown",
        "1 = Ongoing",
        "2 = Completed",
        "3 = Licensed",
        "4 = Publishing finished",
        "5 = Cancelled",
        "6 = On hiatus"
    ]
    with open(path, 'w') as writer:
        writer.write(json.dumps(data))

# Adapted from https://github.com/tachiyomiorg/tachiyomi-extensions/blob/master/src/all/mangadex/src/eu/kanade/tachiyomi/extension/all/mangadex/MangaDexFactory.kt#L54-L96
class Language(Enum):
    """List of MangaDex languages"""

    # The reason why in the end of each variables here
    # has "#:", because to showed up in sphinx documentation.
    English = 'en' #:
    Japanese = 'ja' #:
    Polish = 'pl' #:
    SerboCroatian = 'sh' #:
    Dutch = 'nl' #:
    Italian = 'it' #:
    Russian = 'ru' #:
    German = 'de' #:
    Hungarian = 'hu' #:
    French = 'fr' #:
    Finnish = 'fi' #:
    Vietnamese = 'vi' #:
    Greek = 'el' #:
    Bulgarian = 'bg' #:
    SpanishSpain = 'es' #:
    PortugueseBrazil = 'pt-br' #:
    PortuguesePortugal = 'pt' #:
    Swedish = 'sv' #:
    Arabic = 'ar' #:
    Danish = 'da' #:
    ChineseSimplified = 'zh' #:
    Bengali = 'bn' #:
    Romanian = 'ro' #:
    Czech = 'cs' #:
    Mongolian = 'mn' #:
    Turkish = 'tr' #:
    Indonesian = 'id' #:
    Korean = 'ko' #:
    SpanishLTAM = 'es-la' #:
    Persian = 'fa' #:
    Malay = 'ms' #:
    Thai = 'th' #:
    Catalan = 'ca' #:
    Filipino = 'tl' #:
    ChineseTraditional = 'zh-hk' #:
    Ukrainian = 'uk' #:
    Burmese = 'my' #:
    Lithuanian = 'lt' #:
    Hebrew = 'he' #:
    Hindi = 'hi' #:
    Norwegian = 'no' #:
    Nepali = 'ne' #:

def get_language(lang):
    try:
        return Language[lang]
    except KeyError:
        pass
    return Language(lang)

def create_chapter_folder(base_path, chapter_title):
    chapter_path = base_path / sanitize_filename(chapter_title)
    if not chapter_path.exists():
        chapter_path.mkdir(exist_ok=True)

    return chapter_path