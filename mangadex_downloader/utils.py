import re
import time
import json
import logging
import sys
from enum import Enum
from .errors import InvalidURL, NotLoggedIn
from .downloader import FileDownloader, _cleanup_jobs
from .network import Net

log = logging.getLogger(__name__)

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
    data['author'] = manga.author
    data['artist'] = manga.artist
    data['description'] = manga.description
    data['genre'] = manga.genres
    data['status'] = manga.status
    with open(path, 'w') as writer:
        writer.write(json.dumps(data))

def _keyboard_interrupt_handler(*args):
    # Downloader are not cleaned up
    for job in _cleanup_jobs:
        job()

    # Logging out
    try:
        Net.requests.logout()
    except NotLoggedIn:
        pass
    log.info("Cleaning up...")

    print("Action interrupted by user", file=sys.stdout)
    sys.exit(0)

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