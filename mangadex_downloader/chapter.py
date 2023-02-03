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
import itertools
from pathvalidate import sanitize_filename

from .user import User
from .language import Language
from .fetcher import (
    get_bulk_chapters,
    get_chapter_images,
    get_chapter,
    get_all_chapters,
    get_unread_chapters
)
from .network import Net, base_url
from .errors import ChapterNotFound, GroupNotFound, UserNotFound
from .group import Group
from .config import config, env
from .utils import convert_int_or_float, get_local_attr
# from . import range as range_mod # range_mod stands for "range module"

log = logging.getLogger(__name__)

class ChapterImages:
    def __init__(
        self,
        chapter,
        start_page=None,
        end_page=None,
        _range=None,
    ) -> None:
        self.chap = chapter
        self.id = chapter.id
        self.data_saver = config.use_compressed_image
        self._images = []
        self._low_images = []
        self._data = None
        self._base_url = None
        self._hash = None
        self.start_page = start_page
        self.end_page = end_page
        self.range = _range
        self.force_https = config.force_https

        self.legacy_range = (start_page or end_page)
    
    def fetch(self):
        data = get_chapter_images(self.id, force_https=self.force_https)
        # Construct image url
        self._data = data
        self._base_url = data.get('baseUrl')
        self._hash = data['chapter']['hash']
        self._images = data['chapter']['data']
        self._low_images = data['chapter']['dataSaver']

    def _check_range_page_legacy(self, page, log_info):
        if self.start_page is not None:
            if not (page >= self.start_page):

                if log_info:
                    log.info("Ignoring page %s as \"start_page\" is %s" % (
                        page,
                        self.start_page
                    ))

                return False

        if self.end_page is not None:
            if not (page <= self.end_page):

                if log_info:
                    log.info("Ignoring page %s as \"end_page\" is %s" % (
                        page,
                        self.end_page
                    ))

                return False

        return True

    def _check_range_page(self, page, log_info):
        if self.legacy_range:
            return self._check_range_page_legacy(page, log_info)

        if self.range is not None and not self.range.check_page(self.chap, page):

            if log_info:
                log.info(f"Ignoring page {page}, because page {page} is in ignored list")

            return False
        
        return True

    def iter(self, log_info=False):
        if self._data is None:
            raise Exception("fetch() is not called")

        quality_mode = 'data-saver' if self.data_saver else 'data'
        images = self._low_images if self.data_saver else self._images

        page = 1
        for img in images:

            if not self._check_range_page(page, log_info):
                page += 1
                continue

            url = '{0}/{1}/{2}/{3}'.format(
                self._base_url,
                quality_mode,
                self._hash,
                img
            )

            yield page, url, img

            page += 1

class AggregateChapter:
    def __init__(self, data) -> None:
        self.id = data.get('id')
        self.chapter = data.get('chapter')
        self.others_id = data.get('others')

class Chapter:
    def __init__(
        self,
        _id=None,
        data=None,
    ):
        if _id and data:
            raise ValueError("_id and data cannot be together")

        if data is None:
            data = get_chapter(_id)['data']

        self.id = data['id']
        self._attr = data['attributes']

        # Get scanlation groups and manga
        rels = data['relationships']

        groups = []
        manga_id = None
        manga_title = None
        user = None
        for rel in rels:
            rel_id = rel['id']
            rel_type = rel['type']
            if rel_type == 'scanlation_group':
                groups.append(Group(data=rel))
            elif rel_type == 'manga':
                manga_id = rel_id
                manga_title = get_local_attr(rel["attributes"]["title"])
            elif rel_type == 'user':
                user = User(data=rel)
        
        if manga_id is None:
            raise RuntimeError(f"chapter {_id} has no manga relationship")

        self.user = user
        self.groups = groups
        self.groups_id = [group.id for group in groups]
        self.manga_id = manga_id
        self.manga_title = manga_title
        self._name = None
        self._simpl_name = None
        self.oneshot = False
        self.use_group_name = not config.no_group_name
        self.use_chapter_title = config.use_chapter_title

        self._lang = Language(self._attr['translatedLanguage'])

        self._parse_name()

    # This was used for any classes or functions that require
    # first positional arguments
    @classmethod
    def from_data(cls, data):
        return cls(data=data)

    @property
    def volume(self):
        vol = self._attr['volume']
        if vol is not None:
            # As far as i know
            # Volume manga are integer numbers, not float
            try:
                return convert_int_or_float(vol)
            except ValueError:
                pass

            # Weird af volume name
            # Example: https://api.mangadex.org/manga/485a777b-e395-4ab1-b262-2a87f53e23c0/aggregate
            # (Take a look volume '3Cxx')
            return vol

        # No volume
        return vol

    def __str__(self) -> str:
        return f"'{self.manga_title}' {self.name}"

    @property
    def chapter(self):
        try:
            return self._attr['chapter'].strip()
        except AttributeError:
            # null value
            return None

    @property
    def title(self):
        return self._attr['title']

    @property
    def pages(self):
        return self._attr['pages']

    @property
    def language(self):
        return self._lang

    def _parse_name(self):
        name = ""
        simpl_name = ""

        if self.title is None:
            lower_title = ""
        else:
            lower_title = self.title.lower()

        if 'oneshot' in lower_title:
            self.oneshot = True
            if self.chapter is not None:
                name += f'Chapter. {self.chapter} '
                simpl_name += f"Ch. {self.chapter} "

            name += 'Oneshot'
            simpl_name += 'Oneshot'
        else:
            # Get combined volume and chapter
            if self.volume is not None:
                name += f'Volume. {self.volume} '
                simpl_name += f"Vol. {self.volume} "

            name += f'Chapter. {self.chapter}'
            simpl_name += f"Ch. {self.chapter}"

        self._name = name.strip()
        self._simpl_name = simpl_name.strip()

    @property
    def name(self):
        """This will return chapter name only"""
        return self._name

    @property
    def simple_name(self):
        """Return simplified chapter name"""
        return self._simpl_name

    def _make_name(self, chap_name):
        name = ""

        if self.use_group_name:
            name += f'[{sanitize_filename(self.groups_name)}] '

        name += chap_name

        # Chapter title
        if self.title and self.use_chapter_title:
            name += f' - {sanitize_filename(self.title)}'
        
        return name

    def get_name(self):
        """This will return chapter name with group name and title"""
        return self._make_name(self._name)

    def get_simplified_name(self):
        """Return simplified name of :meth:`Chapter.get_name()`"""
        return self._make_name(self._simpl_name)

    @property
    def groups_name(self):
        if not self.groups:
            return f'User - {self.user.name}'

        groups = self.groups.copy()

        first_group = groups.pop(0)
        name = first_group.name

        for group in groups:
            name += f' & {group.name}'

        return name

def iter_chapters_feed(manga_id, lang):
    includes = [
        'scanlation_group',
        'user',
        'manga'
    ]
    content_ratings = [
        'safe',
        'suggestive',
        'erotica',
        'pornographic'
    ]
    offset = 0
    limit = 500
    
    while True:
        params = {
            'includes[]': includes,
            'contentRating[]': content_ratings,
            'limit': limit,
            'offset': offset,
            'order[volume]': 'asc',
            'order[chapter]': 'asc',
            'translatedLanguage[]': lang,
            'includeEmptyPages': 0
        }
        r = Net.mangadex.get(f'{base_url}/manga/{manga_id}/feed', params=params)
        d = r.json()

        items = d['data']

        if not items:
            break

        for item in items:
            yield item
        
        offset += len(items)

class IteratorChapter:
    def __init__(
        self,
        chapters,
        manga,
        lang,
        start_chapter=None,
        end_chapter=None,
        start_page=None,
        end_page=None,
        no_oneshot=None,
        groups=None,
        _range=None,
        **kwargs
    ):

        legacy_range = (
            start_chapter or
            end_chapter or
            start_page or
            end_page or
            no_oneshot
        )

        if _range and legacy_range:
            raise ValueError("_range and (start_* or end_* or no_oneshot) cannot be together")

        self.chapters = chapters
        self.manga = manga
        self.language = lang
        self.queue = queue.Queue()
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.start_page = start_page
        self.end_page = end_page
        self.no_oneshot = no_oneshot
        self.groups = None
        self.all_group = False
        self.legacy_range = legacy_range
        self.duplicates = {}
        
        if _range is not None:
            # self.range = range_mod.compile(_range)
            self.range = None
        else:
            self.range = _range

        if groups and groups[0] == "all":
            self.all_group = True
        elif groups:
            self.groups = self._parse_groups(groups)

        log_cache = kwargs.get('log_cache')
        self.log_cache = True if log_cache else False

        if Net.mangadex.check_login():
            self._unread_chapters = get_unread_chapters(manga.id)["data"]
        else:
            self._unread_chapters = []

        self._fill_data()

    def _parse_groups(self, ids):
        groups = []

        for _id in ids:
            group = None

            try:
                group = Group(_id)
            except GroupNotFound:
                # It's not a group
                pass
            else:
                groups.append(group)

            # Check if it's a user
            try:
                group = User(_id)
            except UserNotFound:
                # It's not a user
                pass
            else:
                groups.append(group)

            # It's not a group or user
            # raise error
            if group is None:
                raise GroupNotFound(f"Group or user \"{_id}\" cannot be found")
            
        return groups

    def _check_range_chapter_legacy(self, chap):
        num_chap = chap.chapter
        if num_chap != 'none':
            try:
                num_chap = float(num_chap)
            except ValueError:
                pass
            except TypeError:
                # null value
                pass

        is_number = isinstance(num_chap, float)

        # There is a chance that "Chapter 0" is Oneshot or prologue
        # We need to verify that is valid oneshot chapter
        # if it's valid oneshot chapter
        # then we need to skip start_chapter and end_chapter checking
        if is_number and num_chap > 0.0:
            if self.start_chapter is not None and not (num_chap >= self.start_chapter):
                log.info(f"Ignoring chapter {num_chap}, because chapter {num_chap} is in ignored list")
                return False

            if self.end_chapter is not None and not (num_chap <= self.end_chapter):
                log.info(f"Ignoring chapter {num_chap}, because chapter {num_chap} is in ignored list")
                return False

        if chap.oneshot and self.no_oneshot and not self.all_group:
            log.info("Ignoring oneshot chapter since it's in ignored list")
            return False

        # If chapter 0 is prologue or whatever and not oneshot
        # Re-check start_chapter
        elif not chap.oneshot and is_number:
            if self.start_chapter is not None and not (num_chap >= self.start_chapter):
                log.info(f"Ignoring chapter {num_chap}, because chapter {num_chap} is in ignored list")
                return False

        return True

    def _check_range_chapter(self, chap):
        if self.legacy_range:
            return self._check_range_chapter_legacy(chap)
        
        if self.range is not None and not self.range.check_chapter(chap):
            log.info(f"Ignoring chapter {chap.chapter}, because chapter {chap.chapter} is in ignored list")
            return False

        return True

    def _check_duplicate(self, chap):
        name = f'{chap.volume}:{chap.chapter}'

        try:
            self.duplicates[name]
        except KeyError:
            self.duplicates[name] = chap
        else:
            return True
        
        return False

    def _check_chapter(self, chap):
        num_chap = chap.chapter

        if (
            Net.mangadex.check_login() and 
            config.download_mode == "unread" and
            chap.id in self._unread_chapters
        ):
            log.warning(
                f"Ignoring chapter {chap.get_simplified_name()} because it's marked as read"
            )
            return False

        if not self.all_group and not self.groups and self._check_duplicate(chap):
            log.warning(
                f"Found duplicate {chap.simple_name} from [{chap.groups_name}], ignoring... "
            )
            return False

        # Some manga has chapters where it has no pages / images inside of it.
        # We need to verify it, to prevent error when downloading the manga.
        if chap.pages == 0:
            log.warning("Chapter {0} from group {1} has no images, ignoring...".format(
                chap.chapter,
                chap.groups_name
            ))
            return False

        if self.language == Language.Other and chap.language != Language.Other:
            return False

        if not self._check_range_chapter(chap):
            return False

        # Check blacklisted groups and users
        if chap.groups:
            blacklisted_groups = filter(lambda x: x.id in env.group_blacklist, chap.groups)
            for group in blacklisted_groups:
                log.info(
                    f"Ignoring chapter {chap.chapter}, " \
                    f"because group '{group.name}' is blacklisted"
                )
                return False

        if chap.user and chap.user.id in env.user_blacklist:
            log.info(
                f"Ignoring chapter {chap.chapter}, " \
                f"because user '{chap.user.name}' is blacklisted"
            )
            return False

        # Check if chap.group in self.groups (`--group`)
        if not self.all_group and self.groups:

            group_check = False
            for group in self.groups:

                if isinstance(group, Group):
                    group_type = 'scanlator group'
                    group_names = chap.groups_name

                    if group.id in chap.groups_id:
                        group_check = True
                
                elif isinstance(group, User):
                    group_type = 'user'
                    group_names = chap.user.name

                    if chap.user and group.id == chap.user.id:
                        group_check = True
                
            if not group_check:
                log.info(
                    f"Ignoring chapter {num_chap}, " \
                    f"{group_type} \"{group_names}\" is not match with \"{group.name}\""
                )
                return False

        return True

    def _get_next_chapter(self):
        # Get chapter
        try:
            chap = self.queue.get_nowait()
        except queue.Empty:
            raise StopIteration()

        return chap

    def __iter__(self) -> "IteratorChapter":
        return self

    def __next__(self):
        while True:
            chap = self._get_next_chapter()

            if self.log_cache:
                log.debug(f'Caching Volume. {chap.volume} Chapter. {chap.chapter}')

            if not self._check_chapter(chap):
                continue

            chap_images = ChapterImages(
                chap,
                self.start_page,
                self.end_page,
                self.range,
            )

            return chap, chap_images

    def _fill_data(self):
        def sort_chapter(c):
            try:
                return convert_int_or_float(c.chapter)
            except ValueError:
                return float('nan')

        if config.sort_by == 'chapter':
            self.chapters = sorted(self.chapters, key=sort_chapter)
        
        for chap in self.chapters:
            self.queue.put(chap)

class MangaChapter:
    def __init__(self, manga, lang, chapter=None, all_chapters=False):
        if chapter and all_chapters:
            raise ValueError("chapter and all_chapters cannot be together")
        elif chapter is None and not all_chapters:
            raise ValueError("at least provide chapter or set all_chapters to True")

        self.chapters = []
        self.language = Language(lang)
        self.manga = manga

        if chapter:
            self._parse_volumes_from_chapter(chapter)
        elif all_chapters:
            self._parse_volumes()

    def iter(self, *args, **kwargs):
        return IteratorChapter(
            self.chapters,
            self.manga,
            self.language,
            *args,
            **kwargs
        )

    def _parse_volumes_from_chapter(self, chapter):
        if not isinstance(chapter, Chapter):
            chap = Chapter(chapter)
        else:
            chap = chapter

        self.chapters.append(chap)

    def _parse_volumes(self):
        iterator = iter_chapters_feed(self.manga.id, self.language.value)
        self.chapters = map(Chapter.from_data, iterator)

        if not self.chapters:
            raise ChapterNotFound(
                f"Manga '{self.manga.title}' with {self.language.name} language has no chapters"
            )