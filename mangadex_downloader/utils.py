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
        raise InvalidURL('\"%s\" is not valid MangaDex URL' % url)
    return match.group(1)

def validate_legacy_url(url):
    """Validate old mangadex url and return the id"""
    re_url = re.compile(r'mangadex\.org\/(title|chapter)\/(?P<id>[0-9]{1,})')
    match = re_url.search(url)
    if match is None:
        raise InvalidURL('\"%s\" is not valid MangaDex URL' % url)
    return match.group('id')

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
    for index, author in enumerate(manga.authors):
        if index < (len(manga.authors) - 1):
            authors += author + ","
        else:
            # If this is last index, append author without comma
            authors += author
    data['author'] = authors

    # Parse artists
    artists = ""
    for index, artist in enumerate(manga.artists):
        if index < (len(manga.artists) - 1):
            artists += artist + ","
        else:
            # If this is last index, append artist without comma
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

def create_chapter_folder(base_path, chapter_title):
    chapter_path = base_path / sanitize_filename(chapter_title)
    if not chapter_path.exists():
        chapter_path.mkdir(exist_ok=True)

    return chapter_path