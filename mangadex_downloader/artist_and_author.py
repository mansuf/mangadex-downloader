from .fetcher import get_author

class _Base:
    def __init__(self, _id=None, data=None):
        if not data:
            self.data = get_author(_id)['data']
        else:
            self.data = data

        self.id = self.data['id']
        
        attr = self.data['attributes']

        # Name
        self.name = attr.get('name')

        # Profile photo
        self.image = attr.get('imageUrl')

        # The rest of values
        for key, value in attr.items():
            setattr(self, key, value)

class Artist(_Base):
    pass

class Author(_Base):
    pass