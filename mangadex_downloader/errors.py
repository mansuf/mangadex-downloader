# MIT License

# Copyright (c) 2022 Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

class UserNotFound(MangaDexException):
    """Raised when user are not found in MangaDex"""
    pass

class GroupNotFound(MangaDexException):
    """Raised when scanlator group are not found in MangaDex"""
    pass