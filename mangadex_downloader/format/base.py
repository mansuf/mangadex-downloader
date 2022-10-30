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
import os
from pathvalidate import sanitize_filename
from .utils import verify_sha256
from ..downloader import ChapterPageDownloader
from ..utils import QueueWorker

log = logging.getLogger(__name__)

class BaseFormat:
    def __init__(
        self,
        path,
        manga,
        replace,
        kwargs_iter_chapter_img
    ):
        # "Circular imports" problem
        from ..config import config

        self.config = config
        self.path = path
        self.manga = manga
        self.compress_img = config.use_compressed_image
        self.replace = replace
        self.no_chapter_info = config.no_chapter_info
        self.kwargs_iter = kwargs_iter_chapter_img

    def get_images(self, chap_class, images, path, count):
        imgs = []
        chap = chap_class.chapter
        chap_name = chap_class.get_name()

        # Fetching chapter images
        log.info('Getting %s from chapter %s' % (
            'compressed images' if self.compress_img else 'images',
            chap
        ))
        images.fetch()

        while True:
            error = False
            for page, img_url, img_name in images.iter(log_info=True):
                server_file = img_name

                img_ext = os.path.splitext(img_name)[1]
                img_name = count.get() + img_ext

                img_path = path / img_name

                log.info('Downloading %s page %s' % (
                    chap_name,
                    page
                ))

                # This can be `True`, `False`, or `None`
                # `True`: Verify success, hash matching
                # `False`: Verify failed, hash is not matching
                # `None`: Cannot verify, file is not exist (if `path` argument is given)
                verified = verify_sha256(server_file, img_path)

                if verified is None:
                    replace = False
                else:
                    replace = True if self.replace else not verified
                
                # If file still in intact and same as the server
                # Continue to download the others
                if verified and not self.replace:
                    log.info("File exist and same as file from MangaDex server, cancelling download...")
                    count.increase()
                    imgs.append(img_path)
                    continue
                elif verified == False and not self.replace:
                    # File is not same server, probably modified
                    log.info("File exist and NOT same as file from MangaDex server, re-downloading...")

                downloader = ChapterPageDownloader(
                    img_url,
                    img_path,
                    replace=replace,
                    progress_bar=not self.config.no_progress_bar
                )
                success = downloader.download()
                downloader.cleanup()

                # One of MangaDex network are having problem
                # Fetch the new one, and start re-downloading
                if not success:
                    log.error('One of MangaDex network are having problem, re-fetching the images...')
                    log.info('Getting %s from chapter %s' % (
                        'compressed images' if self.compress_img else 'images',
                        chap
                    ))
                    error = True
                    images.fetch()
                    break
                else:
                    imgs.append(img_path)
                    count.increase()
                    continue
            
            if not error:
                return imgs

    def get_fmt_single_cache(self, manga):
        """Get cached all chapters, total pages, 
        and merged name (ex: Vol. 1 Ch. 1 - Vol. 2 Ch. 2) for any single formats
        """
        total = 0

        # In order to add "next chapter" image mark in end of current chapter
        # We need to cache all chapters
        log.info("Preparing to download...")
        cache = []
        # Enable log cache
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for chap_class, chap_images in manga.chapters.iter(**self.kwargs_iter):
            # Fix #10
            # Some programs wouldn't display images correctly
            # Each chapters has one page that has "Chapter n"
            # This is called "start of the chapter" image
            total += 1

            total += chap_class.pages

            item = [chap_class, chap_images]
            cache.append(item)

        if not cache:
            return None

        # Construct .cbz filename from first and last chapter
        first_chapter = cache[0][0]
        last_chapter = cache[len(cache) - 1][0]
        merged_name = sanitize_filename(first_chapter.simple_name + " - " + last_chapter.simple_name)

        return cache, total, merged_name

    def create_worker(self):
        # If CTRL+C is pressed all process is interrupted, right ?
        # Now when this happens in PDF or ZIP processing, this can cause
        # corrupted files.
        # The purpose of this function is to prevent interrupt from CTRL+C
        # Let the job done safely and then shutdown gracefully
        worker = QueueWorker()
        worker.start()
        return worker

    def main(self):
        """Execute main format

        Subclasses must implement this.
        """
        raise NotImplementedError