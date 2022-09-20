# MIT License

# Copyright (c) 2022 Rahman Yusuf

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
from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import NumberWithLeadingZeros, get_chapter_info
from ..utils import create_directory

log = logging.getLogger(__name__)

class Raw(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga

        # Begin downloading
        for chap_class, images in manga.chapters.iter(**self.kwargs_iter):
            chap_name = chap_class.get_simplified_name()

            chapter_path = create_directory(chap_name, base_path)
            count = NumberWithLeadingZeros(chap_class.pages)

            self.get_images(chap_class, images, chapter_path, count)

class RawVolume(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga

        # Sorting volumes
        log.info("Preparing to download")
        cache = {}
        def append_cache(volume, item):
            try:
                data = cache[volume]
            except KeyError:
                cache[volume] = [item]
            else:
                data.append(item)

        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for chap_class, images in manga.chapters.iter(**kwargs_iter):
            append_cache(chap_class.volume, [chap_class, images])

        # Begin downloading
        for volume, chapters in cache.items():
            num = 0
            for chap_class, images in chapters:
                # Each chapters has one page that has "Chapter n"
                # This is called "start of the chapter" image
                num += 1

                num += chap_class.pages

            count = NumberWithLeadingZeros(num)

            for chap_class, images in chapters:
                # Build volume folder name
                if chap_class.volume is not None:
                    volume = f'Vol. {chap_class.volume}'
                else:
                    volume = 'No Volume'
                
                volume_path = create_directory(volume, base_path)

                # Insert "start of the chapter" image
                img_name = count.get() + '.png'
                img_path = volume_path / img_name

                if not self.no_chapter_info:
                    get_chapter_info(chap_class, img_path, self.replace)
                    count.increase()

                self.get_images(chap_class, images, volume_path, count)

class RawSingle(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga

        result_cache = self.get_fmt_single_cache(manga)

        if result_cache is None:
            # The chapters is empty
            # there is nothing we can download
            return
        
        cache, total, merged_name = result_cache

        count = NumberWithLeadingZeros(total)
        path = base_path / merged_name
        path.mkdir(exist_ok=True)

        for chap_class, images in cache:
            # Insert "start of the chapter" image
            img_name = count.get() + '.png'
            img_path = path / img_name

            if not self.no_chapter_info:
                get_chapter_info(chap_class, img_path, self.replace)
                count.increase()

            self.get_images(chap_class, images, path, count)
