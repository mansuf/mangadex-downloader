from .fetcher import get_group
from .utils import get_local_attr

class Group:
    def __init__(self, group_id=None, data=None):
        if not data:
            self.data = get_group(group_id)['data']
        else:
            self.data = data

        self.id = self.data['id']
        attr = self.data['attributes']

        # Name
        self.name = attr['name']

        # Alternative names
        self.alt_names = [get_local_attr(i) for i in attr['altNames']]

        # is it locked ?
        self.locked = attr['locked']

        # Website
        self.url = attr['website']

        # description
        self.description = attr['description']



