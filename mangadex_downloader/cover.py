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

from .fetcher import get_cover_art
from .language import get_language
from .utils import convert_int_or_float

valid_cover_types = [
    "original",
    "512px",
    "256px",
    "none"
]

default_cover_type = "original"

class CoverArt:
    def __init__(self, cover_id=None, data=None):
        if not data:
            self.data = get_cover_art(cover_id)["data"]
        else:
            self.data = data

        self.id = self.data["id"]
        attr = self.data["attributes"]

        # Description
        self.description = attr["description"]

        # File cover
        self.file = attr["fileName"]

        # Locale
        self.locale = get_language(attr["locale"])

    @property
    def volume(self):
        vol = self.data["attributes"]["volume"]
        if vol is not None:
            # As far as i know
            # Volume manga are integer numbers, not float
            try:
                return convert_int_or_float(vol)
            except ValueError:
                pass

            # Weird af volume name
            # Example: https://api.mangadex.org/manga/485a777b-e395-4ab1-b262-2a87f53e23c0/aggregate
            # (Take a look volume "3Cxx")
            return vol

        # No volume
        return vol