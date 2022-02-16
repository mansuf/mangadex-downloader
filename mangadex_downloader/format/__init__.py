from .tachiyomi import Tachiyomi
from ..errors import InvalidFormat

formats = {
    "tachiyomi": Tachiyomi,
}

default_save_as_format = "tachiyomi"

def get_format(fmt):
    try:
        return formats[fmt]
    except KeyError:
        raise InvalidFormat("invalid save_as format, available are: %s" % set(formats.keys()))