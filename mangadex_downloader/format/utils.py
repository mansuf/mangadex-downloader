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

import hashlib
import json
import logging
import os
import re

from enum import Enum
from ..downloader import FileDownloader
from .. import __repository__

log = logging.getLogger(__name__)

def get_chapter_info(chapter, path, replace):
    # "Circular Imports" problem
    from ..config import config

    log.info(f'Getting chapter info for "{chapter.get_name()}"')
    url = f'https://og.mangadex.org/og-image/chapter/{chapter.id}'
    fd = FileDownloader(
        url,
        path,
        replace=replace,
        progress_bar=not config.no_progress_bar
    )
    fd.download()
    fd.cleanup()

    return path

class NumberWithLeadingZeros:
    """A helper class for parsing numbers with leading zeros

    total argument can be iterable or number
    """
    def __init__(self, total):
        try:
            iter_total = iter(total)
        except TypeError:
            if not isinstance(total, int):
                raise ValueError("total must be iterable or int") from None
            total_num = total
        else:
            total_num = 0
            for _ in iter_total:
                total_num += 1

        self._total = total_num
        self._num = 0

    def reset(self):
        self._num = 0

    def increase(self):
        self._num += 1
    
    def decrease(self):
        self._num -= 1

    def get_without_zeros(self):
        """This will return number without leading zeros"""
        return str(self._num)

    def get(self):
        num_str = str(self._num)
        return num_str.zfill(len(str(self._total)))

class Sha256RegexError(Exception):
    """Raised when regex_sha256 cannot grab sha256 from server_file object"""
    pass

def verify_sha256(server_file, path=None, data=None):
    """Verify MangaDex images file

    Parameters
    -----------
    server_file: :class:`str`
        Original MangaDex image filename containing sha256 hash
    path: Optional[Union[:class:`str`, :class:`bytes`, :class:`pathlib.Path`]]
        File want to be verified
    data: Optional[:class:`bytes`]
        Image data wants to be verified
    """
    if path is None and data is None:
        raise ValueError("at least provide path or data")
    elif path and data:
        raise ValueError("path and data cannot be together")

    # Yes this is very cool regex
    regex_sha256 = r'-(?P<hash>.{1,})\.'

    # Get sha256 hash from server file
    match = re.search(regex_sha256, server_file)
    if match is None:
        raise Sha256RegexError(
            f'Failed to grab sha256 hash from server_file = {server_file}. ' \
            f'Please report it to {__repository__}/issues'
        )
    
    server_hash = match.group('hash')
    
    local_sha256 = hashlib.sha256()

    if path:
        # File is not exist
        if not os.path.exists(path):
            return None

        # Begin verifying
        size = 8192
        with open(path, 'rb') as reader:
            while True:
                data = reader.read(size)
                if not data:
                    break

                local_sha256.update(data)
    elif data:
        local_sha256.update(data)
    
    return local_sha256.hexdigest() == server_hash

# Compliance with Tachiyomi local JSON format
class MangaStatus(Enum):
    Ongoing = "1"
    Completed = "2"
    Hiatus = "6"
    Cancelled = "5"

def write_tachiyomi_details(manga, path):
    """Write 'details.json' for tachiyomi format
    
    See https://tachiyomi.org/help/guides/local-manga/#editing-local-manga-details
    """
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