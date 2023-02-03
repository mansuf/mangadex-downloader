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

from .fetcher import get_list

# Why "MangaDexList" ? why not "List" ?
# to prevent typing.List conflict
class MangaDexList:
    def __init__(self, _id=None, data=None):
        if _id is not None:
            data = get_list(_id)['data']

        self.id = data.get('id')
        self.data = data

        attr = data['attributes']

        self.name = attr.get('name')

        self.visibility = attr.get('visibility')

    def total(self) -> int:
        """Return total manga in the list"""
        rels = self.data['relationships']

        count = 0
        for rel in rels:
            _type = rel['type']
            
            if _type == "manga":
                count += 1

        return count

    def __str__(self) -> str:
        return f'MDList: {self.name} ({self.total()} total)'

    def __repr__(self) -> str:
        return f'MDList: {self.name} ({self.total()} total)'

    def iter_manga(self):
        """Yield :class:`Manga` from a list"""
        # "Circular imports" problem
        from .iterator import IteratorMangaFromList

        return IteratorMangaFromList(data=self.data.copy())

