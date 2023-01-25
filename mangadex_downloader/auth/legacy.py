import logging

from .base import MangaDexAuthBase
from ..errors import LoginFailed

log = logging.getLogger(__name__)

class LegacyAuth(MangaDexAuthBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.token = {
            "token": {
                "session": None,
                "refresh": None,
            }
        }

    def _make_ready_token(self, token):
        return {
            "session": token["token"]["session"],
            "refresh": token["token"]["refresh"]
        }

    def update_token(self, session=None, refresh=None):
        if session:
            self.token["token"]["session"] = session
        
        if refresh:
            self.token["token"]["refresh"] = refresh

    def login(self, username, email, password):
        if not username and not email:
            raise LoginFailed("at least provide \"username\" or \"email\" to login")

        # Raise error if password length are less than 8 characters
        if len(password) < 8:
            raise LoginFailed("password length must be more than 8 characters")

        url = f'{self.session.base_url}/auth/login'
        data = {"password": password}
        
        if username:
            data['username'] = username
        if email:
            data['email'] = email
        
        # Begin to log in
        r = self.session.post(url, json=data)
        if r.status_code == 401:
            result = r.json()
            err = result["errors"][0]["detail"]
            log.error("Login to MangaDex failed, reason: %s" % err)
            raise LoginFailed(err)
        
        self.token = r.json()

        return self._make_ready_token(self.token)
    
    def logout(self):
        self.session.post(f"{self.session.base_url}/auth/logout")

        self.token = None
    
    def check_login(self):
        url = f"{self.session.base_url}/auth/check"
        r = self.session.get(url)

        return r.json()['isAuthenticated']

    def refresh_token(self):
        url = f"{self.session.base_url}/auth/refresh"
        r = self.session.post(
            url, json={"token": self.token["token"]["refresh"]}
        )
        result = r.json()

        if r.status_code != 200:
            raise LoginFailed("Refresh token failed, reason: %s" % result["errors"][0]["detail"])
        
        self.token = result
        
        return self._make_ready_token(self.token)