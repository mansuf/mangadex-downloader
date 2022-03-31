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

def get_mark_image(chap, cache, index, start=False):
    text = ""
    additional_info = True
    if start:
        text += "Start: %s\n\n" % chap.name
        chapter = chap
    else:
        text += "Finished: %s\n" % chap.name
        try:
            next_chap = cache[index + 1][1]
        except IndexError:
            chapter = chap
            text += '\n'
            additional_info = False
        else:
            text += "Next: %s\n\n" % next_chap.name
            chapter = next_chap

    if additional_info:
        # Add chapter language
        text += "Language: %s\n" % chapter.get_lang_key()

        if chapter.group is not None:
            # Add scanlation group name
            text += "Translated by: %s" % chapter.group

    font = ImageFont.truetype(font_family, font_size)
    img = Image.new(image_mode, image_size, rgb_white)
    draw = ImageDraw.Draw(img, image_mode)
    draw.text(text_pos, text, rgb_black, font, align='center')

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

    def increase(self):
        self._num += 1
    
    def decrease(self):
        self._num -= 1

    def get_without_zeros(self):
        """This will return number without leading zeros"""
        return self._num

    def get(self):
        num_str = str(self._num)
        return num_str.zfill(len(str(self._total)))