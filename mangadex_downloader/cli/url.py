# MIT License

# Copyright (c) 2022 Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os
import re
import requests

from .utils import get_key_value, check_group_all
from .command import registered_commands
from ..config import config
from ..network import Net
from ..fetcher import get_chapter, get_list, get_manga
from ..errors import ChapterNotFound, InvalidManga, InvalidMangaDexList, InvalidURL, MangaDexException
from ..utils import (
    validate_url as get_uuid,
    find_md_urls,
    valid_url_types
)
from ..main import (
    download as dl_manga,
    download_chapter as dl_chapter,
    download_list as dl_list,
    download_legacy_chapter as dl_legacy_chapter,
    download_legacy_manga as dl_legacy_manga
)

log = logging.getLogger(__name__)

def download_manga(url, args, legacy=False):
    check_group_all(args)

    if args.group and args.no_group_name:
        raise MangaDexException("--group cannot be used together with --no-group-name")

    if args.start_chapter is not None and args.end_chapter is not None:
        if args.start_chapter > args.end_chapter:
            raise MangaDexException("--start-chapter cannot be more than --end-chapter")

    if args.start_page is not None and args.end_page is not None:
        if args.start_page > args.end_page:
            raise MangaDexException("--start-page cannot be more than --end-page")

    # We cannot allow if --range and other range options (such as: --start-chapter) together
    range_forbidden_args = {
        'start_chapter': '--start-chapter',
        'end_chapter': '--end-chapter',
        'start_page': '--start-page',
        'end_page': '--end-page',
        'no_oneshot_chapter': '--no-oneshot-chapter'
    }
    for name, arg in range_forbidden_args.items():
        value = getattr(args, name)
        if args.range and value:
            raise MangaDexException(f'--range cannot be used together with {arg}')

    if config.download_mode == "unread" and not Net.mangadex.check_login():
        raise MangaDexException("You must logged in, in order to use --download-mode=unread")

    args = (
        url,
        args.replace,
        args.start_chapter,
        args.end_chapter,
        args.start_page,
        args.end_page,
        args.no_oneshot_chapter,
        args.use_alt_details,
        args.group,
        args.range,
    )

    if legacy:
        dl_legacy_manga(*args)
    else:
        dl_manga(*args)
        

def download_chapter(url, args, legacy=False):

    if args.range:
        raise MangaDexException('--range option is not available for chapter download')

    if config.download_mode == "unread" and not Net.mangadex.check_login():
        raise MangaDexException("You must logged in, in order to use --download-mode=unread")

    args = (
        url,
        args.replace,
        args.start_page,
        args.end_page,
    )

    if legacy:
        dl_legacy_chapter(*args)
    else:
        dl_chapter(*args)

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
    elif args.range:
        _error_list('--range')

    check_group_all(args)

    if args.group and args.no_group_name:
        raise MangaDexException("--group cannot be used together with --no-group-name")

    if config.download_mode == "unread" and not Net.mangadex.check_login():
        raise MangaDexException("You must logged in, in order to use --download-mode=unread")

    dl_list(
        url,
        args.replace,
        args.group,
    )

# Legacy support
download_legacy_manga = lambda url, args: download_manga(url, args, True)
download_legacy_chapter = lambda url, args: download_chapter(url, args, True)

funcs = {i: globals()['download_%s' % i.replace('-', '_')] for i in valid_url_types}

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
    log.info(f"Checking url = {url}")
    func = None
    _id = None
    
    result = find_md_urls(url)
    if result:
        _id, _type = result
        func = funcs[_type]
    
    # If none of patterns is match, grab UUID instantly and then
    # fetch one by one, starting from manga, list, and then chapter.
    if func is None and _id is None:
        _id = get_uuid(url)

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
            raise InvalidURL(f"'{url}' is not valid MangaDex URL")
    
    return URL(func, _id)

def _try_read(path):
    if not os.path.exists(path):
        return None
    
    with open(path, 'r') as o:
        return o.read()

def build_url(parser, args):
    exec_command = False
    for arg, command_cls in registered_commands.items():
        value = getattr(args, arg)
        if value:
            command = command_cls(parser, args, args.URL)
            result = command.prompt(args.input_pos)

            exec_command = True
            break
    
    if not exec_command:
        # Parsing file path
        if args.file:
            _, file = get_key_value(args.URL, sep=':')
            
            if not file:
                parser.error("Syntax error: file path argument is empty")

            # web URL location support for "file:{location}" syntax
            if file.startswith('http://') or file.startswith('https://'):
                r = Net.requests.get(file)
                try:
                    r.raise_for_status()
                except requests.HTTPError:
                    raise MangaDexException(f"Failed to connect '{file}', status code = {r.status_code}")

                urls = r.text
            
            # Because this is specified syntax for batch downloading
            # If file doesn't exist, raise error
            else:
                urls = _try_read(file)
                if urls is None:
                    parser.error(f"File '{file}' is not exist")
        else:
            file_content = _try_read(args.URL)

            if file_content is not None:
                urls = file_content
            else:
                urls = args.URL

        result = urls.splitlines(keepends=False)

    def yeet():
        """Function to yeet each url with error handling (:class:`InvalidURL`)"""
        if args.type:
            func = lambda i: build_URL_from_type(args.type, i)
        else:
            func = smart_select_url
        
        for i in result:
            try:
                yield func(i)
            except InvalidURL as e:
                log.error(e)
                continue

    # Finally, make :class:`URL` object
    args.URL = yeet()

    # Make sure to check if args.URL is empty
    # if empty exit the program
    if not args.URL:
        parser.error("the following arguments are required: URL")