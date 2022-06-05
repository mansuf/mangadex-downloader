class MangaDexException(Exception):
    """Base exception for MangaDex errors"""
    pass

class UnhandledHTTPError(MangaDexException):
    """Raised when we unable to handle HTTP errors"""
    pass

class HTTPException(MangaDexException):
    """HTTP errors"""
    def __init__(self, *args: object, resp=None) -> None:
        self.response = resp
        super().__init__(*args)

class ChapterNotFound(MangaDexException):
    """Raised when selected manga has no chapters"""
    pass

class InvalidMangaDexList(MangaDexException):
    """Raised when invalid MangaDex list is found"""
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

class InvalidFormat(MangaDexException):
    """Raised when invalid format is given"""
    pass

class PillowNotInstalled(MangaDexException):
    """Raised when trying to download in PDF format but Pillow is not installed"""
    pass

class NotAllowed(MangaDexException):
    """Raised when user trying to download porn manga without `unsafe` enabled"""
    pass

class UserNotFound(MangaDexException):
    """Raised when user are not found in MangaDex"""
    pass

class GroupNotFound(MangaDexException):
    """Raised when scanlator group are not found in MangaDex"""
    pass