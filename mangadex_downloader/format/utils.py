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
text_pos = (150, int(500 / 1.25))
text_align = "center"

def get_mark_image(chap_name, cache, index):
    text = ""
    text += "Finished: " + chap_name
    try:
        next_chap_name = cache[index + 1]
    except IndexError:
        pass
    else:
        text += "\n" + "Next: " + next_chap_name[2]

    font = ImageFont.truetype(font_family, font_size)
    img = Image.new(image_mode, image_size, rgb_white)
    draw = ImageDraw.Draw(img, image_mode)
    draw.text(text_pos, text, rgb_black, font, align='center')

    return img