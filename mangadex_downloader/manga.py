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
from enum import Enum
from typing import List

from .fetcher import get_manga
from .network import uploads_url
from .language import Language, get_details_language
from .utils import get_local_attr, input_handle
from .artist_and_author import Author, Artist
from .cover import CoverArt
from .chapter import MangaChapter
from .tag import Tag

log = logging.getLogger(__name__)

class ContentRating(Enum):
    Safe = 'safe'
    Suggestive = 'suggestive'
    Erotica = 'erotica'
    Pornographic = 'pornographic'

def _append_authors(cls, data, array):
    try:
        created = cls(data=data)
    except KeyError:
        # Although the manga data should never contain 
        # ghost authors or artists (showing just the id, the rest of data is not exist)
        # but at some cases it does
        # Reference: https://api.mangadex.org/manga/2da3ec2b-870f-4f2b-8d53-3b6481dafc32?includes[]=artist
        # (look at relationships artist 'e0e534c8-360c-4709-97b5-718f667a7cd5')
        return
    
    array.append(created)

def _make_cover_art(data):
    try:
        return CoverArt(data=data)
    except KeyError:
        # Ghost cover detected
        # cover id is exist but the rest of data is not
        # Reference: https://api.mangadex.org/manga/ee6106b1-4915-4ba3-aced-7f980848f615?includes[]=cover_art
        return

class Manga:
    def __init__(self, data=None, _id=None, use_alt_details=False):
        if _id and data:
            raise ValueError("_id and data cannot be together")

        if _id:
            self._data = get_manga(_id)['data']
        else:
            self._data = data

        # Append some additional informations
        rels = self._data['relationships']
        authors = []
        artists = []
        cover_art = None
        for rel in rels:
            _type = rel.get('type')

            if _type == 'author':
                _append_authors(Author, rel, authors)

            elif _type == 'artist':
                _append_authors(Artist, rel, artists)

            elif _type == 'cover_art':
                cover_art = _make_cover_art(rel)

        self._artists = artists
        self._authors = authors
        self._cover = cover_art
        self._attr = self._data.get('attributes')
        self._use_alt_details = use_alt_details
        self._chapters = None
        self._altTitles = self._attr.get('altTitles')
        self._orig_title = get_local_attr(self._attr.get('title'))
        self._title = self._parse_title()
        self._description = self._parse_description()

        # An DownloadTracker for manga
        # Value will be filled in `main.py` module
        self.tracker = None

    @property
    def id(self):
        """:class:`str`: ID manga"""
        return self._data.get('id')

    @property
    def title(self):
        """:class:`str`: Return title of the manga"""
        return self._title

    @property
    def alternative_titles(self):
        """List[:class:`str`]: List of alternative titles"""
        titles = self._attr.get('altTitles')
        return [get_local_attr(i) for i in titles]
    
    @property
    def description(self):
        """:class:`str`: Description manga"""
        return self._description

    @property
    def authors(self):
        """List[:class:`str`]: Author of the manga"""
        return [i.name for i in self._authors]

    @property
    def artists(self):
        """List[:class:`str`]: Artist of the manga"""
        return [i.name for i in self._artists]

    @property
    def chapters(self):
        """:class:`MangaChapter`: All chapters manga (if exist)"""
        return self._chapters

    @property
    def cover(self):
        """:class:`CoverArt`: Volume cover"""
        return self._cover

    @property
    def genres(self):
        """List[:class:`str`]: Genres of the manga"""
        new_tags = []
        tags = self._attr.get('tags')
        for tag in tags:
            attr = tag.get('attributes')
            name = get_local_attr(attr.get('name'))
            group = attr.get('group')

            # Aim for genre
            if group == 'genre':
                new_tags.append(name)
        return new_tags
    
    @property
    def status(self):
        """:class:`str`: Status of the manga"""
        return self._attr.get('status').capitalize()

    @property
    def content_rating(self):
        """:class:`ContentRating`: Return content rating of the manga"""
        return ContentRating(self._attr.get('contentRating'))

    @property
    def translated_languages(self) -> List[Language]:
        """List[:class:`Language`]: Return available translated languages of the manga"""
        return [Language(i) for i in self._attr.get('availableTranslatedLanguages')]
    
    @property
    def tags(self) -> List[Tag]:
        """Return tags of the manga"""
        return [Tag(i) for i in self._attr.get('tags')]

    def __repr__(self):
        return self.title

    def _parse_title(self):
        title = self._attr.get('title')
        alt_titles = self._altTitles

        if not self._use_alt_details:
            return get_local_attr(title)

        # The manga doesn't have alternative titles
        if not alt_titles and self._use_alt_details:
            log.info("Manga \"%s\" has no alternative titles" % get_local_attr(title))
            return  get_local_attr(title)

        # Append choices for user input
        choices = {}
        for count, data in enumerate(alt_titles, start=1):
            for alt_title in data.values():
                choices[str(count)] = alt_title
        
        # Append the original title
        count += 1
        choices[str(count)] = get_local_attr(title)

        print("Manga \"%s\" has alternative titles, please choose one" % get_local_attr(title))

        def print_choices():
            for count, data in enumerate(alt_titles, start=1):
                for lang, alt_title in data.items():
                    language = get_details_language(lang)
                    print('(%s). [%s]: %s' % (count, language.name, alt_title))
            
            # Append the original title
            count += 1
            for lang, orig_title in title.items():
                language = get_details_language(lang)
                print('(%s). [%s]: %s' % (count, language.name, orig_title))

        print_choices()

        # User input
        while True:
            choice = input_handle("=> ")
            try:
                title = choices[choice]
            except KeyError:
                print('Invalid choice, try again')
                print_choices()
                continue
            else:
                return title

    def _parse_description(self):
        description = self._attr.get('description')

        if not self._use_alt_details:
            return get_local_attr(description)

        # The manga has no description
        if not description:
            return ""
        
        # The manga has only 1 description
        if len(description) <= 1:
            return get_local_attr(description)
        
        # Append choices for user input
        choices = {}
        for count, desc in enumerate(description.values(), start=1):
            choices[str(count)] = desc
        
        print("Manga \"%s\" has alternative descriptions, please choose one" % self._orig_title)

        def print_choices():
            count = 1
            for lang, desc in description.items():
                language = get_details_language(lang)
                print('(%s). [%s]: %s' % (count, language.name, (desc[:90] + '...')))
                count += 1

        print_choices()

        # User input
        while True:
            choice = input_handle("=> ")
            try:
                desc = choices[choice]
            except KeyError:
                print('Invalid choice, try again')
                print_choices()
                continue
            else:
                return desc

    def fetch_chapters(self, lang, chapter=None, all_chapters=False):
        """Fetch chapters of this manga.
        
        When initializing :class:`Manga`, :attr:`Manga.chapter` is filled with ``None``. 
        Calling this function will fetch the chapters and fill :attr:`Manga.chapter` with 
        :class:`MangaChapter`.
        """
        self._chapters = MangaChapter(self, lang, chapter, all_chapters)