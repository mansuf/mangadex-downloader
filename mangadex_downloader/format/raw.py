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
import os

from .base import BaseFormat
from .utils import (
    NumberWithLeadingZeros,
    get_chapter_info,
    verify_sha256,
    create_file_hash_sha256,
    get_volume_cover
)
from ..utils import create_directory, delete_file

log = logging.getLogger(__name__)

# TODO: PLEASE REFACTOR THIS CODE (Raw, RawVolume, RawSingle)
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
            failed_images = []
            chap_name = chap_class.get_simplified_name()

            file_info = self.get_fi_chapter_fmt(chap_name, chap_class.id)
            chapter_path = create_directory(chap_name, base_path)

            for im_info in file_info.images:
                verified = verify_sha256(im_info.hash, chapter_path / im_info.name)
                if not verified:
                    failed_images.append(im_info)
                
            if failed_images and file_info.completed:
                log.warning(
                    f"Found {len(failed_images)} unverified or missing images from {chap_name}. " \
                    "Re-downloading..."
                )

                # Delete unverified images
                for im_info in failed_images:
                    im_path = chapter_path / im_info.name

                    log.debug(f"Removing unverified image '{im_path.resolve()}'")
                    delete_file(im_path)
            elif file_info.completed:
                log.info(f"'{chap_name}' is verified. no need to re-download")
                self.mark_read_chapter(chap_class)
                continue

            count = NumberWithLeadingZeros(chap_class.pages)

            images = self.get_images(chap_class, images, chapter_path, count)

            for im in images:
                basename = os.path.basename(im)
                im_hash = create_file_hash_sha256(im)
                manga.tracker.add_image_info(
                    chap_name, basename, im_hash, chap_class.id
                )

            manga.tracker.toggle_complete(chap_name, True)

            self.mark_read_chapter(chap_class)
        
        log.info("Waiting for chapter read marker to finish")
        self.cleanup()

class RawVolume(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        tracker = manga.tracker
        file_info = None

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        cache = self.get_fmt_volume_cache(manga)

        # Begin downloading
        for volume, chapters in cache.items():
            failed_images = []
            total = self.get_total_pages_for_volume_fmt(chapters)

            count = NumberWithLeadingZeros(total)

            # Build volume folder name
            if volume is not None:
                volume_name = f'Volume {volume}'
            else:
                volume_name = 'No Volume'

            volume_path = create_directory(volume_name, base_path)
            file_info = self.get_fi_volume_or_single_fmt(volume_name, null_images=False)
            new_chapters = self.get_new_chapters(file_info, chapters, volume_name)

            # Create volume cover
            if self.config.use_volume_cover:
                img_name = count.get() + ".png"
                img_path = volume_path / img_name

                get_volume_cover(manga, volume, img_path, self.replace)
                count.increase()

            # Only checks if ``file_info.complete`` state is True
            if new_chapters and file_info.completed:
                # Re-create directory to prevent error
                shutil.rmtree(volume_path, ignore_errors=True)
                volume_path = create_directory(volume_name, base_path)

            for im_info in file_info.images:
                verified = verify_sha256(im_info.hash, volume_path / im_info.name)
                if not verified:
                    failed_images.append(im_info)
                
            if failed_images and file_info.completed and not new_chapters:
                log.warning(
                    f"Found {len(failed_images)} unverified or missing images from {volume_name}. " \
                    "Re-downloading..."
                )

                # Delete unverified images
                for im_info in failed_images:
                    im_path = volume_path / im_info.name

                    log.debug(f"Removing unverified image '{im_path.resolve()}'")
                    delete_file(im_path)
            elif file_info.completed:
                log.info(f"'{volume_name}' is verified. no need to re-download")
                self.mark_read_chapter(*chapters)
                continue

            # Chapters that have images that are failed to verify
            # (hash is not matching)
            chapter_failed_images = set(i.chapter_id for i in failed_images)

            for chap_class, images in chapters:
                if chap_class.id not in chapter_failed_images and file_info.completed:
                    count.increase(chap_class.pages)
                    continue

                img_name = count.get() + '.png'
                img_path = volume_path / img_name

                # Insert chapter info (cover) image
                if self.config.use_chapter_cover:
                    get_chapter_info(self.manga, chap_class, img_path)
                    count.increase()

                images = self.get_images(chap_class, images, volume_path, count)

                tracker.add_chapter_info(
                    volume_name,
                    chap_class.name,
                    chap_class.id,
                )

                for im in images:
                    basename = os.path.basename(im)
                    im_hash = create_file_hash_sha256(im)
                    manga.tracker.add_image_info(
                        volume_name,
                        basename,
                        im_hash,
                        chap_class.id
                    )
                
                self.mark_read_chapter(chap_class)

            tracker.toggle_complete(volume_name, True)
        
        log.info("Waiting for chapter read marker to finish")
        self.cleanup()

class RawSingle(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        tracker = manga.tracker
        file_info = None
        failed_images = []

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        result_cache = self.get_fmt_single_cache(manga)

        if result_cache is None:
            # The chapters is empty
            # there is nothing we can download
            log.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return
        
        cache, total, name = result_cache

        count = NumberWithLeadingZeros(total)

        path = create_directory(name, base_path)
        file_info = self.get_fi_volume_or_single_fmt(name, null_images=False)
        new_chapters = self.get_new_chapters(file_info, cache, name)

        # Only checks if ``file_info.complete`` state is True
        if new_chapters and file_info.completed:
            # Re-create directory to prevent error
            shutil.rmtree(path, ignore_errors=True)
            path = create_directory(name, base_path)

        for im_info in file_info.images:
            verified = verify_sha256(im_info.hash, path / im_info.name)
            if not verified:
                failed_images.append(im_info)
            
        if failed_images and file_info.completed and not new_chapters:
            log.warning(
                f"Found {len(failed_images)} unverified or missing images from {name}. " \
                "Re-downloading..."
            )

            # Delete unverified images
            for im_info in failed_images:
                im_path = path / im_info.name

                log.debug(f"Removing unverified image '{im_path.resolve()}'")
                delete_file(im_path)
        elif file_info.completed:
            log.info(f"'{name}' is verified. no need to re-download")
            self.mark_read_chapter(*cache)

            log.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        # Chapters that have images that are failed to verify
        # (hash is not matching)
        chapter_failed_images = [i.chapter_id for i in failed_images]

        for chap_class, images in cache:
            if chap_class.id not in chapter_failed_images and file_info.completed:
                count.increase(chap_class.pages)
                continue

            # Insert chapter info (cover) image
            img_name = count.get() + '.png'
            img_path = path / img_name

            if self.config.use_chapter_cover:
                get_chapter_info(self.manga, chap_class, img_path)
                count.increase()

            images = self.get_images(chap_class, images, path, count)

            tracker.add_chapter_info(
                name,
                chap_class.name,
                chap_class.id,
            )

            for im in images:
                basename = os.path.basename(im)
                im_hash = create_file_hash_sha256(im)
                manga.tracker.add_image_info(
                    name,
                    basename,
                    im_hash,
                    chap_class.id
                )
            
            self.mark_read_chapter(chap_class)
        
        tracker.toggle_complete(name, True)

        log.info("Waiting for chapter read marker to finish")
        self.cleanup()