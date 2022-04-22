import logging
import os
import time
import textwrap

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
font_family = "arial.ttf"
font_size = 30
image_size = (720, int(1100 / 1.25))
image_mode = "RGB"
text_pos = (150, int(450 / 1.25))
text_align = "center"

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

    font = ImageFont.truetype(font_family, font_size)
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
        else:
            break
    if err is not None:
        raise err