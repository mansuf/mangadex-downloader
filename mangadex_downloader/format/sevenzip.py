# MIT License

# Copyright (c) 2022-present Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os

from .base import ConvertedChaptersFormat, ConvertedVolumesFormat, ConvertedSingleFormat
from .utils import get_chapter_info, get_volume_cover
from ..utils import create_directory
from ..progress_bar import progress_bar_manager as pbm

try:
    import py7zr
except ImportError:
    PY7ZR_OK = False
else:
    PY7ZR_OK = True


class py7zrNotInstalled(Exception):
    """Raised when py7zr is not installed"""

    pass


log = logging.getLogger(__name__)


class SevenZipFile:
    file_ext = ".cb7"

    def check_dependecies(self):
        if not PY7ZR_OK:
            raise py7zrNotInstalled("py7zr is not installed")

    def convert(self, images, path):
        pbm.set_convert_total(len(images))
        progress_bar = pbm.get_convert_pb(recreate=not pbm.stacked)

        for im_path in images:
            with py7zr.SevenZipFile(
                path, "a" if os.path.exists(path) else "w"
            ) as zip_obj:
                zip_obj.write(im_path, im_path.name)
                progress_bar.update(1)

    def check_write_chapter_info(self, path, target):
        if not os.path.exists(path):
            return True

        with py7zr.SevenZipFile(path, "r") as zip_obj:
            return target not in zip_obj.getnames()

    def insert_ch_info_img(self, images, chapter, path, count):
        """Insert chapter info (cover) image"""
        img_name = count.get() + ".png"
        img_path = path / img_name

        if self.config.use_chapter_cover:
            get_chapter_info(self.manga, chapter, img_path)
            images.append(img_path)
            count.increase()

    def insert_vol_cover_img(self, images, volume, path, count):
        """Insert volume cover"""
        img_name = count.get() + ".png"
        img_path = path / img_name

        if self.config.use_volume_cover:
            get_volume_cover(self.manga, volume, img_path, self.replace)
            images.append(img_path)
            count.increase()


class SevenZip(ConvertedChaptersFormat, SevenZipFile):
    def on_finish(self, file_path, chapter, images):
        chap_name = chapter.get_simplified_name()

        pbm.logger.info(f"{chap_name} has finished download, converting to cb7...")
        self.worker.submit(lambda: self.convert(images, file_path))


class SevenZipVolume(ConvertedVolumesFormat, SevenZipFile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # See `PDFVolume.__init__()` why i did this
        self.images = []

    def on_prepare(self, file_path, volume, count):
        self.images.clear()

        volume_name = self.get_volume_name(volume)
        self.volume_path = create_directory(volume_name, self.path)

        self.insert_vol_cover_img(self.images, volume, self.volume_path, count)

    def on_iter_chapter(self, file_path, chapter, count):
        self.insert_ch_info_img(self.images, chapter, self.volume_path, count)

    def on_received_images(self, file_path, chapter, images):
        self.images.extend(images)

    def on_convert(self, file_path, volume, images):
        volume_name = self.get_volume_name(volume)

        pbm.logger.info(f"{volume_name} has finished download, converting to cb7...")
        self.worker.submit(lambda: self.convert(self.images, file_path))


class SevenZipSingle(ConvertedSingleFormat, SevenZipFile):
    def __init__(self, *args, **kwargs):
        # See `PDFVolume.__init__()` why i did this
        self.images = []

        self.images_path = None

        super().__init__(*args, **kwargs)

    def on_prepare(self, file_path, base_path):
        self.images.clear()

        self.images_path = base_path

    def on_iter_chapter(self, file_path, chapter, count):
        self.insert_ch_info_img(self.images, chapter, self.images_path, count)

    def on_received_images(self, file_path, chapter, images):
        self.images.extend(images)
        return super().on_received_images(file_path, chapter, images)

    def on_finish(self, file_path, images):
        pbm.logger.info(
            f"Manga '{self.manga.title}' has finished download, converting to cbz..."
        )

        self.worker.submit(lambda: self.convert(self.images, file_path))
