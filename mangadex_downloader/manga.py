from .network import uploads_url

# This is shortcut to extract data from weird dict structure
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
    def __init__(self, data):
        self._data = data.get('data')
        self._artists = data.get('artists')
        self._authors = data.get('authors')
        self._cover = data.get('cover_art')
        self._attr = self._data.get('attributes')
        self._chapters = None

    @property
    def id(self):
        """:class:`str`: ID manga"""
        return self._data.get('id')
    
    @property
    def title(self):
        """:class:`str`: Return title of the manga"""
        return _get_attr(self._attr.get('title'))

    @property
    def alternative_titles(self):
        """List[:class:`str`]: List of alternative titles"""
        titles = self._attr.get('altTitles')
        return [_get_attr(i) for i in titles]
    
    @property
    def description(self):
        """:class:`str`: Description manga"""
        return _get_attr(self._attr.get('description'))

    @property
    def authors(self):
        """List[:class:`str`]: Author of the manga"""
        # return self._author['data']['attributes']['name']
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