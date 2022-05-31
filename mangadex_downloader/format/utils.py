import hashlib
import json
import logging
import os
import re
from shutil import ignore_patterns
import sys
import threading
import time
import textwrap

from pathlib import Path
import traceback

from ..errors import MangaDexException
from .. import __repository__

log = logging.getLogger(__name__)

try:
    from PIL import (
        Image,
        ImageDraw,
        ImageFont,
    )
except ImportError:
    pass

rgb_white = (255, 255, 255)
rgb_black = (0, 0, 0)
font_family = 'arial.ttf'
font_size = 30
image_size = (720, int(1100 / 1.25))
image_mode = "RGB"
text_pos = (150, int(450 / 1.25))
text_align = "center"

# For some reason, filename font are case-sensitive
list_font_family = [
    font_family,
    font_family.capitalize(),
    "FreeSans.ttf"
]

def load_font():
    for font in list_font_family:
        try:
            return ImageFont.truetype(font, font_size)
        except OSError as e:
            err_msg = str(e)
            if 'cannot open resource' in err_msg:
                # Font not found
                continue
            
            # Other error
            raise e from None

    log.warning(f"Failed to load {list_font_family} fonts, falling back to default font")
    return None

def get_mark_image(chapter):
    text = ""

    # Current chapter (Volume. n Chapter. n)
    text += chapter.name + '\n'

    # Title chapter
    if chapter.title is not None:
        text += chapter.title

    # an empty line
    text += "\n\n"

    # Add chapter language
    text += "Language: %s\n" % chapter.language.name

    text +=  f"Translated by: {chapter.groups_name}"

    font = load_font()

    img = Image.new(image_mode, image_size, rgb_white)
    draw = ImageDraw.Draw(img, image_mode)

    try:
        draw.multiline_text(text_pos, text, rgb_black, font, align='center')
    except Exception as e:
        log.error(f"Failed to create chapter {chapter.chapter} info, reason: {e.__class__.__name__}: {str(e)}")
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        raise MangaDexException(
            f"An error occurred during creation chapter {chapter.chapter} info. " \
            "Please make sure Arial font is available on your OS (or FreeSans font in Linux)"
        ) from None

    return img

class NumberWithLeadingZeros:
    """A helper class for parsing numbers with leading zeros

    total argument can be iterable or number
    """
    def __init__(self, total):
        try:
            iter_total = iter(total)
        except TypeError:
            if not isinstance(total, int):
                raise ValueError("total must be iterable or int") from None
            total_num = total
        else:
            total_num = 0
            for _ in iter_total:
                total_num += 1

        self._total = total_num
        self._num = 0

    def reset(self):
        self._num = 0

    def increase(self):
        self._num += 1
    
    def decrease(self):
        self._num -= 1

    def get_without_zeros(self):
        """This will return number without leading zeros"""
        return str(self._num)

    def get(self):
        num_str = str(self._num)
        return num_str.zfill(len(str(self._total)))

# Helper function to delete file
def delete_file(file):
    # If 5 attempts is failed to delete file (ex: PermissionError, or etc.)
    # raise error
    err = None
    for attempt in range(5):
        try:
            os.remove(file)
        except Exception as e:
            log.debug("Failed to delete file \"%s\", reason: %s. Trying... (attempt: %s)" % (
                file,
                str(e),
                attempt 
            ))
            err = e
            time.sleep(0.3)
            continue
        else:
            break
    if err is not None:
        raise err

class DuplicateError(Exception):
    pass

class FileTracker:
    """An utility to tracking files
    
    Will be used for any "single" and "volume" format
    """
    def __init__(self, name, base_path=None):
        self.path = base_path
        self.name = name

        if self.path is not None:
            file = base_path
        else:
            file = Path('.')

        file /= ('.' + name + '.tracker.json')
        self.file = file

        self.data = None

        # For thread-safe operations during read & write
        self._lock = threading.Lock()

    def exists(self):
        return self.file.exists()

    def _create_file(self):
        if not self.exists():
            self.file.write_text(json.dumps(
                {"files": []}
            ))

    def close(self):
        if self.exists():
            delete_file(self.file)

    def reset(self):
        if self.exists():
            delete_file(self.file)
        
        self._create_file()

    def _load(self):
        with self._lock:
            self._create_file()

            data = None
            err = None
            for _ in range(5):
                try:
                    data = json.loads(self.file.read_text())
                except json.JSONDecodeError as e:
                    err = e
                    self.reset()
                else:
                    break

            if data is None:
                raise RuntimeError(f"Failed to load tracker file {self.file}, reason: {err}")

            self.data = data

    def check(self, filename):
        self._load()

        files = self.data['files']

        for file in files:
            if file['name'] == filename:
                return True
        
        return False

    def _write(self, data):
        self.file.write_text(json.dumps(data, indent=4))

    def register(self, filename):
        if self.check(filename):
            raise DuplicateError(f"Found duplicate object in {self.file} = {filename}")
        
        with self._lock:
            item = {
                'name': filename
            }

            self.data['files'].append(item)

            self._write(self.data)

        # Update the data
        self._load()

class Sha256RegexError(Exception):
    """Raised when regex_sha256 cannot grab sha256 from server_file object"""
    pass

def verify_sha256(server_file, path=None, data=None):
    """Verify MangaDex images file

    Parameters
    -----------
    server_file: :class:`str`
        Original MangaDex image filename containing sha256 hash
    path: Optional[Union[:class:`str`, :class:`bytes`, :class:`pathlib.Path`]]
        File want to be verified
    data: Optional[:class:`bytes`]
        Image data wants to be verified
    """
    if path is None and data is None:
        raise ValueError("at least provide path or data")
    elif path and data:
        raise ValueError("path and data cannot be together")

    # Yes this is very cool regex
    regex_sha256 = r'-(?P<hash>.{1,})\.'

    # Get sha256 hash from server file
    match = re.search(regex_sha256, server_file)
    if match is None:
        raise Sha256RegexError(
            f'Failed to grab sha256 hash from server_file = {server_file}. ' \
            f'Please report it to {__repository__}/issues'
        )
    
    server_hash = match.group('hash')
    
    local_sha256 = hashlib.sha256()

    if path:
        # File is not exist
        if not os.path.exists(path):
            return None

        # Begin verifying
        size = 8192
        with open(path, 'rb') as reader:
            while True:
                data = reader.read(size)
                if not data:
                    break

                local_sha256.update(data)
    elif data:
        local_sha256.update(data)
    
    return local_sha256.hexdigest() == server_hash
