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
import shutil
from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import NumberWithLeadingZeros, get_chapter_info
from ..utils import create_directory

log = logging.getLogger(__name__)

class Raw(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga

        self.write_tachiyomi_info()

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        # Begin downloading
        for chap_class, images in manga.chapters.iter(**self.kwargs_iter):
            chap_name = chap_class.get_simplified_name()
            self.raw_name = chap_name

            chapter_path = create_directory(chap_name, base_path)
            count = NumberWithLeadingZeros(chap_class.pages)

            self.get_images(chap_class, images, chapter_path, count)

            manga.tracker.toggle_complete(chap_name, True)

class RawVolume(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        tracker = manga.tracker
        file_info = None

        cache = self.get_fmt_volume_cache(manga)

        # Begin downloading
        for volume, chapters in cache.items():
            num = 0
            for chap_class, images in chapters:
                num += 1

                num += chap_class.pages

            count = NumberWithLeadingZeros(num)

            # Build volume folder name
            if volume is not None:
                volume_name = f'Volume {volume}'
            else:
                volume_name = 'No Volume'

            volume_path = create_directory(volume_name, base_path)

            file_info = self.get_fi_volume_or_single_fmt(volume_name)
            
            new_chapters = self.get_new_chapters(file_info, chapters, volume_name)

            # Only checks if ``file_info.complete`` state is True
            if not new_chapters and file_info.completed:
                continue
            elif file_info.completed:
                # Re-create directory to prevent error
                shutil.rmtree(volume_path, ignore_errors=True)
                volume_path = create_directory(volume_name, base_path)

            for chap_class, images in chapters:
                # Insert "start of the chapter" image
                img_name = count.get() + '.png'
                img_path = volume_path / img_name

                if not self.no_chapter_info:
                    get_chapter_info(chap_class, img_path, self.replace)
                    count.increase()

                self.get_images(chap_class, images, volume_path, count)

                tracker.add_chapter_info(
                    volume_name,
                    chap_class.name,
                    chap_class.id,
                )

            tracker.toggle_complete(volume_name, True)

class RawSingle(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        tracker = manga.tracker
        file_info = None

        result_cache = self.get_fmt_single_cache(manga)

        if result_cache is None:
            # The chapters is empty
            # there is nothing we can download
            return
        
        cache, total, name = result_cache

        count = NumberWithLeadingZeros(total)
        path = create_directory(name, base_path)

        file_info = self.get_fi_volume_or_single_fmt(name)
        new_chapters = self.get_new_chapters(file_info, cache, name)

        # Only checks if ``file_info.complete`` state is True
        if not new_chapters and file_info.completed:
            return
        elif file_info.completed:
            # Re-create directory to prevent error
            shutil.rmtree(path, ignore_errors=True)
            path = create_directory(name, base_path)

        for chap_class, images in cache:
            # Insert "start of the chapter" image
            img_name = count.get() + '.png'
            img_path = path / img_name

            if not self.no_chapter_info:
                get_chapter_info(chap_class, img_path, self.replace)
                count.increase()

            self.get_images(chap_class, images, path, count)

            tracker.add_chapter_info(
                name,
                chap_class.name,
                chap_class.id,
            )