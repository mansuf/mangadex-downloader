from .raw import Raw, RawSingle, RawVolume
from .pdf import PDF, PDFSingle
from .tachiyomi import Tachiyomi, TachiyomiZip
from .comic_book import ComicBookArchive, ComicBookArchiveSingle
from ..errors import InvalidFormat

formats = {
    "raw": Raw,
    "raw-volume": RawVolume,
    "raw-single": RawSingle,
    "tachiyomi": Tachiyomi,
    "tachiyomi-zip": TachiyomiZip,
    "pdf": PDF,
    "pdf-single": PDFSingle,
    "cbz": ComicBookArchive,
    "cbz-single": ComicBookArchiveSingle
}

default_save_as_format = "tachiyomi"

def get_format(fmt):
    try:
        return formats[fmt]
    except KeyError:
        raise InvalidFormat("invalid save_as format, available are: %s" % set(formats.keys()))