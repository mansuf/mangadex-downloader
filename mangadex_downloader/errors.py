class MangadexError(BaseException):
    """Base Exception"""
    pass

class FetcherError(MangadexError):
    """Raised when error happened during fetching manga"""
    pass

class MangaNotFound(MangadexError):
    """Raised when given manga is not exist"""
    pass

class UserBanned(MangadexError):
    """Raised when user are banned from mangadex"""
    pass