from .fetcher import get_user

class User:
    def __init__(self, user_id=None, data=None):
        if data is None:
            self.data = get_user(user_id)['data']
        else:
            self.data = data

        self.id = self.data['id']
        attr = self.data['attributes']

        self.name = attr['username']
        self.roles = attr['roles']