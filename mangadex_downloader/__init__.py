"""
Download manga from Mangadex through Python
"""

__version__ = "0.3.0"
__description__ = "Download manga from Mangadex through Python"
__author__ = "mansuf"
__license__ = "The Unlicense"
__repository__ = "https://github.com/mansuf/mangadex-downloader"

import logging
from .network import *
from .main import *
from .errors import *
from .manga import Manga

logging.getLogger(__name__).addHandler(logging.NullHandler())