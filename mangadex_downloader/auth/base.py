class MangaDexAuthBase:
    """Base auth class for MangaDex API"""
    def __init__(self, session, login_cache, config_enabled):
        self.session = session
        self.login_cache = login_cache
        self.config_enabled = config_enabled

    def login(self):
        """Login to MangaDex"""
        pass

    def logout(self):
        """Logout from MangaDex
        
        NOTE: this method only revoke `session_token` and `refresh_token`
        """
        pass

    def refresh_token(self):
        """Get new `session_token` using `refresh_token`"""
        pass

    def check_login(self):
        """Check if login session is still active"""
        pass