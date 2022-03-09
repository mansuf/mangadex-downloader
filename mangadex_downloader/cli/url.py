import logging
import re

from ..fetcher import get_chapter, get_list, get_manga
from ..errors import ChapterNotFound, InvalidManga, InvalidMangaDexList, InvalidURL, MangaDexException
from ..utils import validate_url
from ..main import (
    download as dl_manga,
    download_chapter as dl_chapter,
    download_list as dl_list
)

log = logging.getLogger(__name__)

# Helper for building smart select url regex
def _build_re(_type):
    # Base url
    regex = r"mangadex\.org\/%s\/([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})" % _type
    return re.compile(regex)

def download_manga(url, args):
    dl_manga(
        url,
        args.folder,
        args.replace,
        args.use_compressed_image,
        args.start_chapter,
        args.end_chapter,
        args.start_page,
        args.end_page,
        args.no_oneshot_chapter,
        args.language,
        args.cover,
        args.save_as
    )

def download_chapter(url, args):
    dl_chapter(
        url,
        args.folder,
        args.replace,
        args.start_page,
        args.end_page,
        args.use_compressed_image,
        args.save_as
    )

def _error_list(option):
    raise MangaDexException("%s is not allowed when download a list" % option)

def download_list(url, args):
    if args.start_chapter:
        _error_list('--start-chapter')
    elif args.end_chapter:
        _error_list('--end-chapter')
    elif args.start_page:
        _error_list('--start-page')
    elif args.end_page:
        _error_list('--end-page')

    dl_list(
        url,
        args.folder,
        args.replace,
        args.use_compressed_image,
        args.language,
        args.cover,
        args.save_as
    )

valid_types = [
    "manga",
    "list",
    "chapter"
]

funcs = {i: globals()['download_%s' % i] for i in valid_types}

regexs = {i: _build_re(i) for i in valid_types}

class URL:
    def __init__(self, func, _id):
        self.func = func
        self.id = _id
    
    def __call__(self, args, _type=None):
        if _type is not None:
            self.func = funcs[_type]
        self.func(self.id, args)

    def __repr__(self) -> str:
        return '<URL func = "%s" id = "%s">' % (
            self.func.__name__,
            self.id
        )

def build_URL_from_type(_type, _id):
    return URL(funcs[_type], _id)

def smart_select_url(url):
    """Wisely determine type url. The process is checking given url one by one"""
    log.info("Checking url...")
    found = False
    func = None
    _id = None
    for _type, regex in regexs.items():
        # Match pattern regex
        match = re.search(regex, url)
        if match is None:
            continue

        # Get UUID
        _id = match.group(1)

        # Get download function
        func = funcs[_type]

        found = True
    
    # If none of patterns is match, grab UUID instantly and then
    # fetch one by one, starting from manga, list, and then chapter.
    if not found:
        _id = validate_url(url)

        # Manga
        try:
            get_manga(_id)
        except InvalidManga:
            pass
        else:
            func = funcs['manga']
        
        # MDlist
        try:
            get_list(_id)
        except InvalidMangaDexList:
            pass
        else:
            func = funcs['list']

        # Chapter
        try:
            get_chapter(_id)
        except ChapterNotFound:
            pass
        else:
            func = funcs['chapter']

        # None of them is found in MangaDex
        # raise error
        if func is None:
            raise InvalidURL("Invalid MangaDex url")
    
    return URL(func, _id)