import logging
from enum import Enum

from .fetcher import get_manga
from .network import uploads_url
from .language import get_details_language
from .utils import get_local_attr, input_handle
from .artist_and_author import Author, Artist
from .cover import CoverArt

log = logging.getLogger(__name__)

class ContentRating(Enum):
    Safe = 'safe'
    Suggestive = 'suggestive'
    Erotica = 'erotica'
    Pornographic = 'pornographic'

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
                authors.append(Author(data=rel))

            elif _type == 'artist':
                artists.append(Artist(data=rel))

            elif _type == 'cover_art':
                cover_art = CoverArt(data=rel)

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

    @property
    def id(self):
        """:class:`str`: ID manga"""
        return self._data.get('id')

    def __str__(self):
        return self.title

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
        """:class:`Chapter`: All chapters manga (if exist)"""
        return self._chapters

    @property
    def cover_art(self):
        """:class:`str`: Original cover manga"""
        return '{0}/covers/{1}/{2}'.format(
            uploads_url,
            self.id,
            self._cover.file
        )
    
    @property
    def cover_art_512px(self):
        """:class:`str`: 512px wide thumbnail cover manga"""
        return '{0}/covers/{1}/{2}.512.jpg'.format(
            uploads_url,
            self.id,
            self._cover.file
        )

    @property
    def cover_art_256px(self):
        """:class:`str`: 256px wide thumbnail cover manga"""
        return '{0}/covers/{1}/{2}.256.jpg'.format(
            uploads_url,
            self.id,
            self._cover.file
        )

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
