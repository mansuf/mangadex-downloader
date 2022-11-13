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
def get_all_tags(use_requests=False) -> List[Tag]:
    # See validator for env MANGADEXDL_TAGS_BLACKLIST
    # We cannot use `requestsMangaDexSession` (Net.mangadex)
    # because of "Circular imports" problem
    # smh
    if use_requests:
        session = Net.requests
    else:
        session = Net.mangadex

    tags = []
    r = session.get(f'{base_url}/manga/tag')
    data = r.json()

    for item in data['data']:
        tags.append(Tag(item))
    
    return tags