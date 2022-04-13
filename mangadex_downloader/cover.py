from .fetcher import get_cover_art
from .utils import File
from .language import get_language

class CoverArt:
    def __init__(self, cover_id=None, data=None):
        if not data:
            self.data = get_cover_art(cover_id)['data']
        else:
            self.data = data

        self.id = self.data['id']
        attr = self.data['attributes']

        # Description
        self.description = attr['description']

        # Volume
        self.volume = attr['volume']

        # File cover
        self.file = File(attr['fileName'])

        # Locale
        self.locale = get_language(attr['locale'])