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
import re

from .mdlist import MangaDexList
from .errors import HTTPException, InvalidURL, MangaDexException, NotLoggedIn
from .network import Net, base_url
from .manga import ContentRating, Manga
from .fetcher import get_list
from .user import User
from .language import get_language
from .config import ConfigTypeError, _validate_bool as validate_boolean
from .utils import validate_url, get_local_attr

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
        raise NotImplementedError

class SearchFilterError(MangaDexException):
    def __init__(self, key, msg):
        text = f"Search filter error '{key}' = {msg}"

        super().__init__(text)

class IteratorManga(BaseIterator):
    def __init__(
        self,
        title,
        authors=None,
        artists=None,
        year=None,
        included_tags=None,
        included_tags_mode=None,
        excluded_tags=None,
        excluded_tags_mode=None,
        status=None,
        original_language=None,
        excluded_original_language=None,
        available_translated_language=None,
        publication_demographic=None,
        content_rating=None,
        created_at_since=None,
        updated_at_since=None,
        has_available_chapters=None,
        group=None,
        order=None
    ):
        super().__init__()

        _default_content_ratings = [
            'safe',
            'suggestive',
            'erotica',
            'pornographic'
        ]

        self.limit = 100
        self.title = title

        # Validation
        value_and_or = ['AND', 'OR']

        if year:
            m = re.match(r'[0-9]{4}')
            if not m:
                raise SearchFilterError(
                    "year",
                    f"value must be integer and length must be 4"
                )

        _locals = locals()
        def validate_tags_mode(key):
            value = _locals[key]
            if value and value.upper() not in value_and_or:
                raise SearchFilterError(
                    key,
                    f"value must be 'OR' or 'AND', not '{value}'"
                )

        validate_tags_mode("included_tags_mode")
        validate_tags_mode("excluded_tags_mode")

        def validate_uuid(key):
            new_values = []
            values = _locals[key]
            if values is None:
                return
            
            if isinstance(values, str):
                values = [values]
            
            for value in values:
                # Get the id
                try:
                    _id = validate_url(value)
                except InvalidURL:
                    raise SearchFilterError(
                        key,
                        f"'{value}' is not valid UUID"
                    )
                else:
                    new_values.append(_id)
            
            return new_values

        group = validate_uuid("group")

        tags = self._get_tags()
        def validate_tags(key):
            new_values = []
            values = _locals[key]
            if values is None:
                return

            if isinstance(values, str):
                values = [values]

            # Lowercase to prevent error
            values = [i.lower() for i in values]

            for value in values:
                # Try to match the keyword tags
                try:
                    _id = tags[value]
                except KeyError:
                    pass
                else:
                    new_values.append(_id)
                    continue

                # Try to get uuid
                try:
                    _id = validate_url(value)
                except InvalidURL:
                    raise SearchFilterError(
                        key,
                        f"'{value}' is not valid keyword or uuid tag"
                    )
                
                new_values.append(_id)
            
            return new_values

        included_tags = validate_tags("included_tags")
        excluded_tags = validate_tags("excluded_tags")

        def validate_values_from_list(key, array):
            values = _locals[key]
            if values is None:
                return
            
            if isinstance(values, str):
                values = [values]

            for value in values:
                if value.lower() not in array:
                    raise SearchFilterError(
                        key,
                        f"Value must be one of {array}, not {value}"
                    )

        _status_values = [
            'ongoing',
            'completed',
            'hiatus',
            'cancelled'
        ]
        validate_values_from_list("status", _status_values)

        def validate_language(key):
            new_values = []
            values = _locals[key]
            if values is None:
                return

            if isinstance(values, str):
                values = [values]

            for value in values:
                try:
                    lang = get_language(value)
                except ValueError as e:
                    raise SearchFilterError(key, e)
                else:
                    new_values.append(lang.value)
        
            return new_values
        
        original_language = validate_language("original_language")
        excluded_original_language = validate_language("excluded_original_language")
        available_translated_language = validate_language("available_translated_language")

        _pub_demo_values = [ 
            'shounen',
            'shoujo',
            'josei',
            'seinen',
            'none'
        ]
        validate_values_from_list("publication_demographic", _pub_demo_values)

        _content_rating_values = [a.value for a in ContentRating]
        validate_values_from_list("content_rating", _content_rating_values)

        if has_available_chapters:
            try:
                validate_boolean(has_available_chapters)
            except ConfigTypeError as e:
                raise SearchFilterError("has_available_chapters", e)

        # Validate orders
        def validate_order(order):
            new_order = {}
            ascending = ['asc', 'ascending']
            descending = ['desc', 'descending']
            for key, value in order.items():
                # Validate order keys
                re_order_key = r'order\[(' \
                               r'title|' \
                               r'year|' \
                               r'createdAt|' \
                               r'updatedAt|' \
                               r'latestUploadedChapter|' \
                               r'followedCount|' \
                               r'relevance|' \
                               r'rating|' \
                               r')\]'
                match = re.match(re_order_key, key)
                if match is None:
                    raise SearchFilterError(
                        key,
                        "Invalid order key"
                    )

                if value in ascending:
                    new_order[key] = ascending[0]
                elif value in descending:
                    new_order[key] = descending[0]
                else:
                    raise SearchFilterError(
                        key,
                        f"invalid value must be one of {ascending} or {descending}"
                    )
            
            return new_order

        order = validate_order(order)

        self._param_init = {
            "authors[]": authors,
            "artists[]": artists,
            "year": year,
            "includedTags[]": included_tags,
            "includedTagsMode": included_tags_mode,
            "excludedTags[]": excluded_tags,
            "excludedTagsMode": excluded_tags_mode,
            "status[]": status,
            "originalLanguage[]": original_language,
            "excludedOriginalLanguage[]": excluded_original_language,
            "availableTranslatedLanguage[]": available_translated_language,
            "publicationDemographic[]": publication_demographic,
            "contentRating[]": content_rating or _default_content_ratings,
            "createdAtSince": created_at_since,
            "updatedAtSince": updated_at_since,
            "hasAvailableChapters": has_available_chapters,
            "group": group,
        }

        self._param_init.update(**order)

    def _get_tags(self):
        tags = {}
        r = Net.mangadex.get(f'{base_url}/manga/tag')
        data = r.json()

        for item in data['data']:
            _id = item['id']
            attr = item['attributes']
            name = get_local_attr(attr['name']).lower()
            tags[name] = _id
        
        return tags

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

    def next(self) -> Manga:
        return self.queue.get_nowait()

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

class IteratorUserLibraryManga(BaseIterator):
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
            manga = self.queue.get_nowait()

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

class IteratorMangaFromList(BaseIterator):
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
    
    def next(self) -> Manga:
        while True:
            manga = self.queue.get_nowait()
            
            return manga
    
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

    def next(self) -> MangaDexList:
        return self.queue.get_nowait()

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
    
    def next(self) -> MangaDexList:
        return self.queue.get_nowait()

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

    def next(self) -> MangaDexList:
        return self.queue.get_nowait()

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

def iter_random_manga(content_ratings):
    ids = []
    while True:
        params = {
            'includes[]': ['author', 'artist', 'cover_art'],
            "contentRating[]": content_ratings
        }
        r = Net.mangadex.get(f'{base_url}/manga/random', params=params)
        data = r.json()['data']
        manga = Manga(data=data)

        if manga.id not in ids:
            # Make sure it's not duplicated manga
            ids.append(manga.id)
            yield manga

        continue