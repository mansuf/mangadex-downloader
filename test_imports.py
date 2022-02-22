print("Importing main module")
from mangadex_downloader import __version__, download

print("Importing cli module")
from mangadex_downloader.__main__ import main

print("Test imports mangadex-downloader v%s is success" % __version__)