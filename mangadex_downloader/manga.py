import logging

from .network import uploads_url
from .language import get_details_language

log = logging.getLogger(__name__)

# This is shortcut to extract data from local dict structure
# in MangaDex JSON data
# For example: 
# {
#     'attributes': {
#         'en': '...' # This is what we need 
#     }
# }
def _get_attr(data):
    if not data:
        return ""
    for key, val in data.items():
        return val

class Manga:
    def __init__(self, data, use_alt_details=False):
        self._data = data.get('data')
        self._artists = data.get('artists')
        self._authors = data.get('authors')
        self._cover = data.get('cover_art')
        self._attr = self._data.get('attributes')
        self._use_alt_details = use_alt_details
        self._chapters = None
        self._altTitles = self._attr.get('altTitles')
        self._orig_title = _get_attr(self._attr.get('title'))
        self._title = self._parse_title()
        self._description = self._parse_description()

    @property
    def id(self):
        """:class:`str`: ID manga"""
        return self._data.get('id')
    
    def _parse_title(self):
        title = self._attr.get('title')
        alt_titles = self._altTitles

        if not self._use_alt_details:
            return _get_attr(title)

        # The manga doesn't have alternative titles
        if not alt_titles and self._use_alt_details:
            log.info("Manga \"%s\" has no alternative titles" % _get_attr(title))
            return  _get_attr(title)

        # Append choices for user input
        choices = {}
        for count, data in enumerate(alt_titles, start=1):
            for alt_title in data.values():
                choices[str(count)] = alt_title
        
        # Append the original title
        count += 1
        choices[str(count)] = _get_attr(title)

        print("Manga \"%s\" has alternative titles, please choose one" % _get_attr(title))

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
            choice = input("=> ")
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
            return _get_attr(description)

        # The manga has no description
        if not description:
            return ""
        
        # The manga has only 1 description
        if len(description) <= 1:
            return _get_attr(description)
        
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
            choice = input("=> ")
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
        return [_get_attr(i) for i in titles]
    
    @property
    def description(self):
        """:class:`str`: Description manga"""
        return self._description

    @property
    def authors(self):
        """List[:class:`str`]: Author of the manga"""
        authors = []
        for data in self._authors:
            author = data['data']['attributes']['name']
            authors.append(author)
        return authors
    
    @property
    def artists(self):
        """List[:class:`str`]: Artist of the manga"""
        artists = []
        for data in self._artists:
            artist = data['data']['attributes']['name']
            artists.append(artist)
        return artists

    def _parse_cover_art(self):
        return self._cover['data']['attributes']['fileName']

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
            self._parse_cover_art()
        )
    
    @property
    def cover_art_512px(self):
        """:class:`str`: 512px wide thumbnail cover manga"""
        return '{0}/covers/{1}/{2}.512.jpg'.format(
            uploads_url,
            self.id,
            self._parse_cover_art()
        )

    @property
    def cover_art_256px(self):
        """:class:`str`: 256px wide thumbnail cover manga"""
        return '{0}/covers/{1}/{2}.256.jpg'.format(
            uploads_url,
            self.id,
            self._parse_cover_art()
        )

    @property
    def genres(self):
        """List[:class:`str`]: Genres of the manga"""
        new_tags = []
        tags = self._attr.get('tags')
        for tag in tags:
            attr = tag.get('attributes')
            name = _get_attr(attr.get('name'))
            group = attr.get('group')

            # Aim for genre
            if group == 'genre':
                new_tags.append(name)
        return new_tags
    
    @property
    def status(self):
        """:class:`str`: Status of the manga"""
        return self._attr.get('status').capitalize()