class MangaDexException(Exception):
    """Base exception for MangaDex errors"""
    pass

class HTTPException(MangaDexException):
    """HTTP errors"""
    pass

class InvalidManga(MangaDexException):
    """Raised when invalid manga is found"""
    pass

class InvalidURL(MangaDexException):
    """Raised when given mangadex url is invalid"""
    pass

class LoginFailed(MangaDexException):
    """Raised when login is failed"""
    pass

class AlreadyLoggedIn(MangaDexException):
    """Raised when user try login but already logged in """
    pass

class NotLoggedIn(MangaDexException):
    """Raised when user try to logout when user are not logged in"""
    pass