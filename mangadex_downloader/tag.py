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

from functools import lru_cache
from typing import List

from .network import Net, base_url
from .utils import get_local_attr

class Tag:
    def __init__(self, data):
        self.id = data['id']

        attr = data['attributes']

        self.name = get_local_attr(attr['name'])
        self.description = get_local_attr(attr['description'])
        self.group = attr['group']

    def __repr__(self) -> str:
        return self.name

@lru_cache(maxsize=4096)
def get_all_tags() -> List[Tag]:
    tags = []
    r = Net.mangadex.get(f'{base_url}/manga/tag')
    data = r.json()

    for item in data['data']:
        tags.append(Tag(item))
    
    return tags