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
        total = 0

        # In order to add "next chapter" image mark in end of current chapter
        # We need to cache all chapters
        log.info("Preparing to download...")
        cache = []
        # Enable log cache
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for chap_class, images in manga.chapters.iter(**kwargs_iter):
            # Each chapters has one page that has "Chapter n"
            # This is called "start of the chapter" image
            total += 1

            total += chap_class.pages

            item = [chap_class, images]
            cache.append(item)

        count = NumberWithLeadingZeros(total)

        # Construct folder name from first and last chapter
        first_chapter = cache[0][0]
        last_chapter = cache[len(cache) - 1][0]
        path = base_path / sanitize_filename(first_chapter.simple_name + " - " + last_chapter.simple_name)
        path.mkdir(exist_ok=True)

        for chap_class, images in cache:
            # Insert "start of the chapter" image
            img_name = count.get() + '.png'
            img_path = path / img_name

            if not self.no_chapter_info:
                get_chapter_info(chap_class, img_path, self.replace)
                count.increase()

            self.get_images(chap_class, images, path, count)
