from .raw import Raw, RawSingle, RawVolume
from .pdf import PDF, PDFSingle, PDFVolume
from .comic_book import ComicBookArchive, ComicBookArchiveSingle, ComicBookArchiveVolume
from .sevenzip import SevenZip, SevenZipSingle, SevenZipVolume
from .epub import Epub, EpubSingle, EpubVolume
from ..errors import InvalidFormat

formats = {
    "raw": Raw,
    "raw-volume": RawVolume,
    "raw-single": RawSingle,
    "pdf": PDF,
    "pdf-volume": PDFVolume,
    "pdf-single": PDFSingle,
    "cbz": ComicBookArchive,
    "cbz-volume": ComicBookArchiveVolume,
    "cbz-single": ComicBookArchiveSingle,
    "cb7": SevenZip,
    "cb7-volume": SevenZipVolume,
    "cb7-single": SevenZipSingle,
    "epub": Epub,
    "epub-volume": EpubVolume,
    "epub-single": EpubSingle,
}

deprecated_formats = []

default_save_as_format = "raw"


def get_format(fmt):
    try:
        return formats[fmt]
    except KeyError:
        raise InvalidFormat(
            "invalid save_as format, available are: %s" % set(formats.keys())
        )
