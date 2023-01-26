class MangaDexAuthBase:
    """Base auth class for MangaDex API"""
    def __init__(self, session):
        self.session = session

    def login(self, username, email, password):
        """Login to MangaDex"""
        pass

    def logout(self):
        """Logout from MangaDex
        
        NOTE: this method only revoke `session_token` and `refresh_token`
        """
        pass

    def update_token(self, session=None, refresh=None):
        """Update token internally for this class"""
        pass

    def refresh_token(self):
        """Get new `session_token` using `refresh_token`"""
        pass

    def check_login(self):
        """Check if login session is still active"""
        pass