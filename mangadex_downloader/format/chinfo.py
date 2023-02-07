import sys
import textwrap
from pathlib import Path

from ..utils import get_cover_art_url
from ..network import Net

try:
    from PIL import (
        Image,
        ImageDraw,
        ImageFont,
        ImageEnhance,
        ImageFilter
    )
except ImportError:
    pass

# Font related
rgb_white = (255, 255, 255)
font_family = 'arial.ttf'

# Text positioning
text_align = "left"

base_path = Path(__file__).parent.parent.resolve()
font_path = base_path / "fonts/GNU FreeFont"
if sys.platform == "win32":
    # According to GNUFreeFont README page
    # https://ftp.gnu.org/gnu/freefont/README
    # it is recommended to use "ttf" files for Windows
    font_ext = ".ttf"
    font_path /= "ttf"
else:
    # Otherwise just use "otf" files for other OS
    font_ext = ".otf"
    font_path /= "otf"

fonts = {
    "default": font_path / f"FreeSans{font_ext}",
    "bold": font_path / f"FreeSansBold{font_ext}",
    "bold_italic": font_path / f"FreeSansBoldOblique{font_ext}",
    "italic": font_path / f"FreeSansOblique{font_ext}"
}

def load_font(type, size):
    font = fonts[type]
    loc = str(font.resolve())
    return ImageFont.truetype(loc, size)

def textwrap_newlines(text, width):
    """This function is designed to split with newlines instead of list"""
    new_text = ""
    result = textwrap.wrap(text, width)
    for word in result:
        new_text += word + "\n"

    return new_text

def draw_multiline_text(font, image, text, width_pos, height_pos, split_size):
    new_text = textwrap_newlines(text, width=split_size)
    draw = ImageDraw.Draw(image)
    draw.multiline_text(
        xy=(width_pos, height_pos),
        text=new_text,
        fill=rgb_white,
        font=font,
        align="left"
    )
    return draw.multiline_textbbox((width_pos, height_pos), new_text, font, align="left")

def get_chapter_info(manga, cover, chapter):
    cover_url = get_cover_art_url(manga, cover, "original")
    r = Net.mangadex.get(cover_url, stream=True)
    image = Image.open(r.raw)
    image = image.convert("RGBA")

    # resize image to fixed 1000px width (keeping aspect ratio) so font sizes and text heights match for all covers
    aspect_ratio = image.height / image.width
    new_width = 1000
    new_height = new_width * aspect_ratio

    image = image.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)

    # apply blur and darken filters
    image = image.filter(ImageFilter.GaussianBlur(6))
    image = ImageEnhance.Brightness(image).enhance(0.3)

    title_text = chapter.manga_title
    if len(title_text) > 85:
        title_font = load_font("bold", size=80)
    else:
        title_font = load_font("bold", size=90)
    title_bbox = draw_multiline_text(
        font=title_font,
        image=image,
        text=title_text,
        width_pos=40,
        height_pos=40,
        split_size=20
    )

    chinfo_font = load_font("default", size=45)
    chinfo_text = chapter.simple_name
    if chapter.title:
        chinfo_text += f" - {chapter.title}"
    chinfo_bbox = draw_multiline_text(
        font=chinfo_font,
        image=image,
        text=chinfo_text,
        width_pos=40,
        height_pos=title_bbox[3] + 40,
        split_size=40
    )

    scanlatedby_font = load_font("italic", size=30)
    scanlatedby_text = "Scanlated by:"
    scanlatedby_bbox = draw_multiline_text(
        font=scanlatedby_font,
        image=image,
        text=scanlatedby_text,
        width_pos=40,
        height_pos=chinfo_bbox[3] + 30,
        split_size=40
    )

    group_bbox = None
    for group in chapter.groups:
        group_font = load_font("bold", size=50)
        group_text = group.name
        if group_bbox is None:
            height_pos = scanlatedby_bbox[3] + 15
        else:
            height_pos = group_bbox[3] + 5
        
        group_bbox = draw_multiline_text(
            font=group_font,
            image=image,
            text=group_text,
            width_pos=40,
            height_pos=height_pos,
            split_size=30
        )

    logo = base_path / "images/mangadex-logo.png"
    logo_image = Image.open(logo)
    logo_image = logo_image.convert("RGBA").resize((120, 120))
    image.alpha_composite(
        im=logo_image,
        dest=(40, (image.height - (logo_image.height + 30)))
    )

    return image

