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
from .utils import verify_sha256, write_tachiyomi_details, get_md_file_hash
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

        # I want to change BaseFormat.get_images() parameters
        # for parameter DownloadTracker (BaseFormat.manga.tracker)
        # But, it will require change the entire formats module
        # And since this will be used in raw formats only
        # It takes too much times to working on this (also i'm lazy :P)
        # So i'm gonna store the folder name to this variable instead
        self.raw_name = None

    def get_images(self, chap_class, images, path, count):
        imgs = []
        chap = chap_class.chapter
        chap_name = chap_class.get_name()
        cls_name = self.__class__.__name__
        file_info = None
        tracker = self.manga.tracker
        unverified_images = []
        empty_images = False
        is_raw_fmt = "Raw" == cls_name

        # Do not fetch chapter images when we have tracker file
        # (For raw formats only)
        if is_raw_fmt:
            file_info = tracker.get(self.raw_name)
            log.debug(f"Verifying {self.raw_name} images")

            if file_info is None:
                file_info = tracker.add_file_info(
                    self.raw_name,
                    chap_class.id,
                    null_images=False,
                )

            for im_info in file_info.images:
                verified = verify_sha256(im_info.hash, (path / im_info.name))
                if not verified:
                    unverified_images.append(im_info.name)
            
            if not unverified_images and file_info.completed and file_info.images:
                log.info(
                    f"All images from '{self.raw_name}' is verified. " \
                     "No need to re-download."
                )
                return [path / i.name for i in file_info.images]

            elif not file_info.images:
                # Images are empty (not downloaded yet)
                self.fetch_images(images, chap)
                empty_images = True

            else:
                # Failed to verify or missing images
                total = len(unverified_images) or (chap_class.pages - len(file_info.images))
                log.info(
                    f"Found {total} unverified or missing pages. " \
                    "Re-downloading missing pages..."
                )
                self.fetch_images(images, chap)
                tracker.toggle_complete(self.raw_name, False)
        else:
            self.fetch_images(images, chap)

        while True:
            error = False
            for page, img_url, img_name in images.iter(log_info=True):
                img_hash = get_md_file_hash(img_name)
                img_ext = os.path.splitext(img_name)[1]
                img_name = count.get() + img_ext

                # Ignore verified images
                # (raw formats only)
                if (
                    is_raw_fmt and 
                    not empty_images and 
                    img_name not in unverified_images and
                    file_info.completed
                ):
                    count.increase()
                    continue

                img_path = path / img_name

                log.info('Downloading %s page %s' % (
                    chap_name,
                    page
                ))

                # This can be `True`, `False`, or `None`
                # `True`: Verify success, hash matching
                # `False`: Verify failed, hash is not matching
                # `None`: Cannot verify, file is not exist (if `path` argument is given)
                verified = verify_sha256(img_hash, img_path)

                if verified is None:
                    replace = False
                else:
                    replace = True if self.replace else not verified
                
                # If file still in intact and same as the server
                # Continue to download the others
                if verified and not self.replace:
                    log.info("File exist and same as file from MangaDex server, cancelling download...")

                    if is_raw_fmt:
                        tracker.add_image_info(
                            self.raw_name,
                            img_name,
                            img_hash
                        )

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
                    if is_raw_fmt:
                        tracker.add_image_info(
                            self.raw_name,
                            img_name,
                            img_hash
                        )

                    imgs.append(img_path)
                    count.increase()
                    continue
            
            if not error:
                return imgs

    def fetch_images(self, images, chap):
        # Fetch chapter images
        log.info('Getting %s from chapter %s' % (
            'compressed images' if self.compress_img else 'images',
            chap
        ))
        images.fetch()

    def get_fmt_single_cache(self, manga):
        """Get cached all chapters, total pages, 
        and merged name (ex: Vol. 1 Ch. 1 - Vol. 2 Ch. 2) for any single formats
        """
        total = 0

        log.info("Preparing to download...")
        cache = []
        # Enable log cache
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for chap_class, chap_images in manga.chapters.iter(**self.kwargs_iter):
            # Fix #10
            # Some programs wouldn't display images correctly
            total += 1

            total += chap_class.pages

            item = [chap_class, chap_images]
            cache.append(item)

        if not cache:
            return None

        name = "All chapters"

        return cache, total, name

    def get_fmt_volume_cache(self, manga):
        """Get all cached volumes"""
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
        for chap_class, chap_images in manga.chapters.iter(**kwargs_iter):
            append_cache(chap_class.volume, [chap_class, chap_images])
        
        return cache

    def write_tachiyomi_info(self):
        """Write `details.json` file for tachiyomi app"""
        if self.config.write_tachiyomi_info:
            log.info("Writing tachiyomi `details.json` file")
            write_tachiyomi_details(self.manga, (self.path / "details.json"))

    def get_fi_volume_or_single_fmt(self, name, hash=None):
        """Get DownloadTracker file_info for volume or single format
        
        Create one if it doesn't exist
        """
        tracker = self.manga.tracker
        file_info = tracker.get(name)
        if file_info is None:
            file_info = tracker.add_file_info(
                name=name,
                id=None,
                hash=hash,
                null_images=True,
                null_chapters=False
            )
        
        return file_info

    def get_new_chapters(self, file_info, chapters, name):
        """Retrieve new chapters for volume and single formats"""
        # Check for new chapters in volume
        new_chapters = []
        for chap_class, _ in chapters:
            if chap_class.id not in file_info.chapters:
                new_chapters.append(chap_class.name)

        if new_chapters and file_info.completed:
            log.info(
                f"There is new {len(new_chapters)} chapters in {name}. " \
                f"Re-downloading {name}..."
            )

            # Let output list of new chapters in verbose mode only
            log.debug(f"List of new chapters = {new_chapters}")

        elif file_info.completed:
            log.info(f"There is no new chapters in {name}, ignoring...")

        return new_chapters

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