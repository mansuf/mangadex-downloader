"""
A command-Line tool to download manga from MangaDex, written in Python
"""

__version__ = "2.0.0a"
__description__ = "A Command-line tool to download manga from MangaDex, written in Python"
__author__ = "Rahman Yusuf"
__author_email__ = "danipart4@gmail.com"
__license__ = "MIT"
__repository__ = "mansuf/mangadex-downloader"

import logging
from .network import *
from .main import *
from .errors import *
from .manga import Manga, ContentRating
from .language import Language, get_language

logging.getLogger(__name__).addHandler(logging.NullHandler())