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
import queue

from .mdlist import MangaDexList
from .errors import HTTPException, MangaDexException, NotLoggedIn
from .network import Net, base_url
from .manga import Manga
from .fetcher import (
    get_list,
    get_legacy_id
)
from .user import User
from .filters import Filter
from .utils import check_blacklisted_tags_manga
from .cover import CoverArt
from .forums import iter_md_urls_from_forum_thread
from .chapter import Chapter

log = logging.getLogger(__name__)

class BaseIterator:
    def __init__(self):
        self.queue = queue.Queue()
        self.offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.queue.empty():
            # Maximum number of results from MangaDex API
            if self.offset >= 10000:
                raise StopIteration()
            else:
                self.fill_data()

        try:
            return self.next()
        except queue.Empty:
            raise StopIteration()

    def fill_data(self):
        raise NotImplementedError

    def next(self):
        return self.queue.get_nowait()

class MangaIterator(BaseIterator):
    """Iterator specialized for manga that has abilities like
    
    - Filter tags based on environment MANGADEXDL_TAGS_BLACKLIST
    """
    def next(self):
        while True:
            manga = super().next()

            blacklisted, tags = check_blacklisted_tags_manga(manga)

            if blacklisted:
                log.debug(
                    f'Not showing manga "{manga.title}", ' \
                    f'since it contain one or more blacklisted tags {tags}'
                )
                continue

            return manga

class SearchFilterError(MangaDexException):
    def __init__(self, key, msg):
        text = f"Search filter error '{key}' = {msg}"

        super().__init__(text)

class IteratorManga(MangaIterator):
    def __init__(
        self,
        title,
        **filters
    ):
        super().__init__()

        self.limit = 100
        self.title = title

        f = Filter()
        self._param_init = f.get_request_params(**filters)

    def _get_params(self):
        includes = ['author', 'artist', 'cover_art']

        params = {
            'includes[]': includes,
            'title': self.title,
            'limit': self.limit,
            'offset': self.offset,
        }
        params.update(self._param_init.copy())

        return params

    def fill_data(self):
        params = self._get_params()
        url = f'{base_url}/manga'
        r = Net.mangadex.get(url, params=params)
        data = r.json()

        if r.status_code >= 400:
            err = data['errors'][0]['detail']
            raise MangaDexException(err)

        items = data['data']
        
        for item in items:
            self.queue.put(Manga(data=item))

        self.offset += len(items)

class IteratorUserLibraryManga(MangaIterator):
    statuses = [
        'reading',
        'on_hold',
        'plan_to_read',
        'dropped',
        're_reading',
        'completed'
    ]

    def __init__(self, status=None):
        super().__init__()

        self.limit = 100
        self.offset = 0

        if status is not None and status not in self.statuses:
            raise MangaDexException(f"{status} are not valid status, choices are {set(self.statuses)}")

        self.status = status

        lib = {}
        for stat in self.statuses:
            lib[stat] = []
        self.library = lib

        logged_in = Net.mangadex.check_login()
        if not logged_in:
            raise NotLoggedIn("Retrieving user library require login")

        self._parse_reading_status()

    def _parse_reading_status(self):
        r = Net.mangadex.get(f'{base_url}/manga/status')
        data = r.json()

        for manga_id, status in data['statuses'].items():
            self.library[status].append(manga_id)

    def _check_status(self, manga):
        if self.status is None:
            return True

        manga_ids = self.library[self.status]
        return manga.id in manga_ids

    def next(self) -> Manga:
        while True:
            manga = super().next()

            if not self._check_status(manga):
                # Filter is used
                continue
            
            return manga

    def fill_data(self):
        includes = [
            'artist', 'author', 'cover_art'
        ]
        params = {
            'includes[]': includes,
            'limit': self.limit,
            'offset': self.offset,
        }
        url = f'{base_url}/user/follows/manga'
        r = Net.mangadex.get(url, params=params)
        data = r.json()

        items = data['data']

        for item in items:
            self.queue.put(Manga(data=item))
        
        self.offset += len(items)

class IteratorMangaFromList(MangaIterator):
    def __init__(self, _id=None, data=None):
        if _id is None and data is None:
            raise ValueError("atleast provide _id or data")
        elif _id and data:
            raise ValueError("_id and data cannot be together")

        super().__init__()

        self.id = _id
        self.data = data
        self.limit = 100
        self.name = None # type: str
        self.user = None # type: User

        self.manga_ids = []

        self._parse_list()

    def _parse_list(self):
        if self.id:
            data = get_list(self.id)['data']
        else:
            data = self.data

        self.name = data['attributes']['name']
        
        for rel in data['relationships']:
            _type = rel['type']
            _id = rel['id']
            if _type == 'manga':
                self.manga_ids.append(_id)
            elif _type == 'user':
                self.user = User(_id)
    
    def fill_data(self):
        ids = self.manga_ids
        includes = ['author', 'artist', 'cover_art']
        content_ratings = [
            'safe',
            'suggestive',
            'erotica',
            'pornographic' # Filter porn content will be done in next()
        ]

        limit = self.limit
        if ids:
            param_ids = ids[:limit]
            del ids[:len(param_ids)]
            params = {
                'includes[]': includes,
                'limit': limit,
                'contentRating[]': content_ratings,
                'ids[]': param_ids
            }
            url = f'{base_url}/manga'
            r = Net.mangadex.get(url, params=params)
            data = r.json()

            notexist_ids = param_ids.copy()
            copy_data = data.copy()
            for manga_data in copy_data['data']:
                manga = Manga(data=manga_data)
                if manga.id in notexist_ids:
                    notexist_ids.remove(manga.id)
            
            if notexist_ids:
                for manga_id in notexist_ids:
                    log.warning(f'There is ghost (not exist) manga = {manga_id} in list {self.name}')

            for manga_data in data['data']:
                self.queue.put(Manga(data=manga_data))

class IteratorUserLibraryList(BaseIterator):
    def __init__(self):
        super().__init__()

        self.limit = 100
        self.offset = 0

        logged_in = Net.mangadex.check_login()
        if not logged_in:
            raise NotLoggedIn("Retrieving user library require login")

    def fill_data(self):
        params = {
            'limit': self.limit,
            'offset': self.offset,
        }
        url = f'{base_url}/user/list'
        r = Net.mangadex.get(url, params=params)
        data = r.json()

        items = data['data']

        for item in items:
            self.queue.put(MangaDexList(data=item))
        
        self.offset += len(items)

class IteratorUserList(BaseIterator):
    def __init__(self, _id=None):
        super().__init__()

        self.limit = 100
        self.user = User(_id)
    
    def fill_data(self):
        params = {
            'limit': self.limit,
            'offset': self.offset,
            
        }
        url = f'{base_url}/user/{self.user.id}/list'
        try:
            r = Net.mangadex.get(url, params=params)
        except HTTPException:
            # Some users are throwing server error (Bad gateway)
            # MD devs said it was cache and headers issues
            # Reference: https://api.mangadex.org/user/10dbf775-1935-4f89-87a5-a1f4e64d9d94/list
            # For now the app will throw error and tell the user cannot be fetched until it's get fixed

            # HTTPException from session only giving "server throwing ... code" message
            raise HTTPException(
                f"An error occured when getting mdlists from user \"{self.user.id}\". " \
                f"The app cannot fetch all MangaDex lists from user \"{self.user.id}\" " \
                "because of server error. The only solution is to wait until this get fixed " \
                "from MangaDex itself."
            ) from None

        data = r.json()

        items = data['data']

        for item in items:
            self.queue.put(MangaDexList(data=item))
        
        self.offset += len(items)

class IteratorUserLibraryFollowsList(BaseIterator):
    def __init__(self):
        super().__init__()

        self.limit = 100

        logged_in = Net.mangadex.check_login()
        if not logged_in:
            raise NotLoggedIn("Retrieving user library require login")

    def fill_data(self):
        params = {
            'limit': self.limit,
            'offset': self.offset,
        }
        url = f'{base_url}/user/follows/list'
        r = Net.mangadex.get(url, params=params)
        data = r.json()

        items = data['data']

        for item in items:
            self.queue.put(MangaDexList(data=item))
        
        self.offset += len(items)

class IteratorSeasonalManga(IteratorMangaFromList):
    owner_list = 'd2ae45e0-b5e2-4e7f-a688-17925c2d7d6b'

    def __init__(self, season):
        seasons = self._get_seasons()

        try:
            mdlist = seasons[season]
        except KeyError:
            raise MangaDexException(f"invalid season, available choices are {list(seasons.keys())}")
        
        super().__init__(mdlist.id)

    @classmethod
    def _get_seasons(self):
        seasons = {}
        for mdlist in IteratorUserList(self.owner_list):
            name = mdlist.name.lower().replace('seasonal: ', '')
            seasons[name] = mdlist
        
        return seasons

def iter_random_manga(**filters):
    ids = []
    f = Filter([
        'content_rating',
        'included_tags',
        'included_tags_mode',
        'excluded_tags',
        'excluded_tags_mode'
    ])
    filter_params = f.get_request_params(**filters)
    while True:
        params = {
            'includes[]': ['author', 'artist', 'cover_art'],
        }
        params.update(**filter_params)
        r = Net.mangadex.get(f'{base_url}/manga/random', params=params)
        data = r.json()['data']
        manga = Manga(data=data)

        blacklisted, tags = check_blacklisted_tags_manga(manga)

        if blacklisted:
            log.debug(
                f'Not showing manga "{manga.title}", ' \
                f'since it contain one or more blacklisted tags {tags}'
            )
            continue

        if manga.id not in ids:
            # Make sure it's not duplicated manga
            ids.append(manga.id)
            yield manga

        continue

# For some reason, "/cover" endpoint has result limit for each responses.
# This class is used for getting all covers while respecting result limit.
# Of course, the results will be cached to prevent repeated requests.
class CoverArtIterator(BaseIterator):
    cache = {}

    def __init__(self, manga_id):
        super().__init__()

        self.limit = 100
        self.manga_id = manga_id
        
        if self.cache.get(manga_id) is None:
            # Data is not cached
            self.cache[manga_id] = []
    
    def _make_cache_iterator(self):
        for item in self.cache.get(self.manga_id):
            yield item

    def __iter__(self):
        cache = self.cache.get(self.manga_id)
        if cache:
            # Return cached data instead
            return self._make_cache_iterator()
        else:
            return self

    def fill_data(self):
        # If it's already cached
        # DO NOT FETCH IT AGAIN
        if self.cache.get(self.manga_id):
            return

        # One-shot filling covers in single function call
        # So cache can be used
        while True:
            params = {
                "manga[]": self.manga_id,
                "offset": self.offset,
                "limit": self.limit
            }

            url = f"{base_url}/cover"
            r = Net.mangadex.get(url, params=params)
            items = r.json()["data"]

            if not items:
                break

            for item in items:
                cover = CoverArt(data=item)
                self.queue.put(cover)

                # Add it to cache
                self.cache[self.manga_id].append(cover)
            
            self.offset += len(items)

class ForumThreadMangaDexURLIterator(BaseIterator):
    """If `Fetch` parameter is `True`, it will return object based on returned type URLs. 
    For example:

    - manga = :class:`mangadex_downloader.manga.Manga`
    - chapter = :class:`mangadex_downloader.chapter.Chapter`
    - list = :class:`mangadex_downloader.mdlist.MangaDexList`
    - etc
    
    Otherwise it will return the ids only.
    """
    def __init__(self, thread_id, fetch=False):
        super().__init__()

        self.thread_id = thread_id
        self.fetch = fetch
        self.limit = 5 # We don't want to slow down the application

        self.iterator = iter_md_urls_from_forum_thread(thread_id)

    def _make_item_obj(self, item_id, item_type):
        if item_type == "legacy-manga":
            new_id = get_legacy_id("manga", item_id)
            obj = Manga(_id=new_id)
        elif item_type == "legacy-chapter":
            new_id = get_legacy_id("chapter", item_id)
            obj = Chapter(_id=new_id)
        elif item_type == "list":
            obj = MangaDexList(_id=item_id)
        elif item_type == "manga":
            obj = Manga(_id=item_id)
        elif item_type == "chapter":
            obj = Chapter(_id=item_id)
        else:
            # This should be impossible
            # because `item_type` value is from `utils.valid_url_types`
            raise RuntimeError(f"item_type '{item_type}' unknown, item_id = {item_id}")
        
        return obj

    def fill_data(self):
        current_limit = 0
        while current_limit < self.limit:
            try:
                raw_item = next(self.iterator)
            except StopIteration:
                return

            item_id, item_type = raw_item

            if self.fetch:
                item = self._make_item_obj(item_id, item_type)
            else:
                item = item_id
            
            self.queue.put(item)
            current_limit += 1