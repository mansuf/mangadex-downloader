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
from functools import lru_cache
from .errors import (
    ChapterNotFound,
    GroupNotFound,
    InvalidManga,
    InvalidMangaDexList,
    MangaDexException, 
    UserNotFound
)
from .network import Net, base_url, origin_url
from .utils import validate_url

log = logging.getLogger(__name__)

def get_manga(manga_id):
    url = '{0}/manga/{1}'.format(base_url, manga_id)
    params = {
        'includes[]': ['author', 'artist', 'cover_art']
    }
    r = Net.mangadex.get(url, params=params)
    if r.status_code == 404:
        raise InvalidManga('Manga \"%s\" cannot be found' % manga_id)
    return r.json()

def get_legacy_id(_type, _id):
    supported_types = ['manga', 'chapter', 'title']

    # Alias for title
    if _type == 'manga':
        _type = 'title'

    if _type not in supported_types:
        raise MangaDexException("\"%s\" is not supported type" % _type)

    # Normally, this can be done from API url. But, somehow the API endpoint (/legacy/mapping)
    # throwing server error (500) in response. We will use this, until the API gets fixed.
    # NOTE: The error only applied to "chapter" type, "manga" type is working fine.
    url = '{0}/{1}/{2}'.format(origin_url, _type, _id)

    # The process is by sending request to "mangadex.org" (not "api.mangadex.org"), if it gets redirected,
    # the legacy id is exist. Otherwise the legacy id is not found in MangaDex database
    r = Net.mangadex.get(url, allow_redirects=False)

    if r.status_code >= 300:
        # Redirected request, the legacy id is exist
        location_url = r.headers.get('location')

        # Get the new id
        url = validate_url(location_url)
    else:
        # 200 status code, the legacy id is not exist.
        # Raise error based on type url
        if _type == 'title':
            raise InvalidManga('Manga \"%s\" cannot be found' % _id)
        elif _type == 'chapter':
            raise ChapterNotFound("Chapter %s cannot be found" % _id)

    return url

@lru_cache(maxsize=1048)
def get_author(author_id):
    url = '{0}/author/{1}'.format(base_url, author_id)
    r = Net.mangadex.get(url)
    return r.json()

@lru_cache(maxsize=1048)
def get_user(user_id):
    url = '{0}/user/{1}'.format(base_url, user_id)
    r = Net.mangadex.get(url)
    if r.status_code == 404:
        raise UserNotFound(f"user {user_id} cannot be found")
    return r.json()

@lru_cache(maxsize=1048)
def get_cover_art(cover_id):
    url = '{0}/cover/{1}'.format(base_url, cover_id)
    r = Net.mangadex.get(url)
    return r.json()

def get_chapter(chapter_id):
    url = '{0}/chapter/{1}'.format(base_url, chapter_id)
    params = {
        'includes[]': ['scanlation_group', 'user', 'manga']
    }
    r = Net.mangadex.get(url, params=params)
    if r.status_code == 404:
        raise ChapterNotFound("Chapter %s cannot be found" % chapter_id)
    return r.json()

def get_list(list_id):
    url = '{0}/list/{1}'.format(base_url, list_id)
    r = Net.mangadex.get(url)
    if r.status_code == 404:
        raise InvalidMangaDexList("List %s cannot be found" % list_id)
    return r.json()

@lru_cache(maxsize=1048)
def get_group(group_id):
    url = '{0}/group/{1}'.format(base_url, group_id)
    r = Net.mangadex.get(url)
    if r.status_code == 404:
        raise GroupNotFound(f"Scanlator group {group_id} cannot be found")
    return r.json()

def get_all_chapters(manga_id, lang):
    url = '{0}/manga/{1}/aggregate'.format(base_url, manga_id)
    r = Net.mangadex.get(url, params={'translatedLanguage[]': [lang]})
    return r.json()

def get_chapter_images(chapter_id, force_https=False):
    url = '{0}/at-home/server/{1}'.format(base_url, chapter_id)
    r = Net.mangadex.get(url, params={'forcePort443': force_https})
    return r.json()

def get_bulk_chapters(chap_ids):
    url = '{0}/chapter'.format(base_url)
    includes = ['scanlation_group', 'user']
    content_ratings = [
        'safe',
        'suggestive',
        'erotica',
        'pornographic'
    ]
    params = {
        'ids[]': chap_ids,
        'limit': 100,
        'includes[]': includes,
        'contentRating[]': content_ratings
    }
    r = Net.mangadex.get(url, params=params)
    return r.json()

def get_unread_chapters(manga_id):
    url = f"{base_url}/manga/{manga_id}/read"
    r = Net.mangadex.get(url)
    return r.json()