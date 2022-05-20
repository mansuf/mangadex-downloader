import json
import logging
import os
import threading
import time
import textwrap

from pathlib import Path

from ..errors import MangaDexException

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
]

class FontNotFound(MangaDexException):
    """Raised when loading specified font are not found"""
    pass

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

    raise FontNotFound(f'fonts {list_font_family} are not found')

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
    draw.multiline_text(text_pos, text, rgb_black, font, align='center')

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
