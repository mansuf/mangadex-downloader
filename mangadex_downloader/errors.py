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