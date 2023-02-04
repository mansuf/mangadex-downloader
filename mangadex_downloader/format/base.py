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
from .utils import (
    verify_sha256,
    write_tachiyomi_details,
    get_md_file_hash,
    create_file_hash_sha256,
    QueueWorkerReadMarker
)
from ..downloader import ChapterPageDownloader
from ..utils import QueueWorker, delete_file

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
        self.kwargs_iter = kwargs_iter_chapter_img

        self.chapter_read_marker = QueueWorkerReadMarker(manga.id)

        # Only start worker for chapter read marker
        # if user is logged in and --download-mode is set to unread
        if (
            self.config.download_mode == "unread" and
            self.chapter_read_marker.net.mangadex.check_login()
        ):
            self.chapter_read_marker.start()

    def cleanup(self):
        # Shutdown some worker threads
        self.manga.tracker.shutdown()
        self.chapter_read_marker.shutdown(blocking=True)

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
                
                img_hash = get_md_file_hash(img_name)
                img_ext = os.path.splitext(img_name)[1]
                img_name = count.get() + img_ext

                img_path = path / img_name

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
                    log.debug(f"Page {page} ({img_name}) is exist and verified, cancelling download...")
                    count.increase()
                    imgs.append(img_path)
                    continue
                elif verified == False and not self.replace:
                    # File is not same server, probably modified
                    log.warning(
                        f"Page {page} ({img_name}) is exist but failed to verify (hash is not matching), " \
                        "re-downloading..."
                    )
                
                log.info('Downloading %s page %s' % (
                    chap_name,
                    page
                ))

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

    def mark_read_chapter(self, *chapters):
        """Mark a chapter as read"""
        if (
            self.config.download_mode == "unread" and
            self.chapter_read_marker.net.mangadex.check_login()
        ):
            for chapter in chapters:
                # Dynamic type data at it's finest
                # (I'm just lazy that's it)
                if isinstance(chapter, list) or isinstance(chapter, tuple):
                    chapter = chapter[0]

                if isinstance(chapter, str):
                    self.chapter_read_marker.submit(chapter)
                else:
                    self.chapter_read_marker.submit(chapter.id)

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
            total += chap_class.pages

            item = [chap_class, chap_images]
            cache.append(item)

        if not cache:
            return None

        if self.config.use_chapter_cover:
            total += len(cache)

        name = "All chapters"

        return cache, total, name

    def get_total_pages_for_volume_fmt(self, chapters):
        total = 0

        if self.config.use_volume_cover:
            total += 1

        if self.config.use_chapter_cover:
            total += len(chapters)

        for chap_class, _ in chapters:
            total += chap_class.pages
        
        return total

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

    def get_volume_name(self, vol):
        # Build volume folder name
        if vol is not None:
            name = f'Vol. {vol}'
        else:
            name = 'No Volume'
        
        return name

    def write_tachiyomi_info(self):
        """Write `details.json` file for tachiyomi app"""
        if self.config.write_tachiyomi_info:
            log.info("Writing tachiyomi `details.json` file")
            write_tachiyomi_details(self.manga, (self.path / "details.json"))

    def get_fi_chapter_fmt(self, name, id, hash=None, null_images=False):
        """Get DownloadTracker._FileInfo for chapter format (raw, cbz, epub, etc..)
        
        Create one if it doesn't exist
        """
        tracker = self.manga.tracker
        file_info = tracker.get(name)
        if file_info is None:
            file_info = tracker.add_file_info(
                name=name,
                id=id,
                hash=hash,
                null_images=null_images,
            )

        return file_info

    def get_fi_volume_or_single_fmt(self, name, hash=None, null_images=True):
        """Get DownloadTracker._FileInfo for volume or single format
        
        Create one if it doesn't exist
        """
        tracker = self.manga.tracker
        file_info = tracker.get(name)
        if file_info is None:
            file_info = tracker.add_file_info(
                name=name,
                id=None,
                hash=hash,
                null_images=null_images,
                null_chapters=False
            )
        
        return file_info

    def get_new_chapters(self, file_info, chapters, name, log_output=True):
        """Retrieve new chapters for volume and single formats"""
        # Check for new chapters in volume
        new_chapters = []
        for chap_class, _ in chapters:
            if chap_class.id not in file_info.chapters:
                new_chapters.append(chap_class.name)

        if new_chapters and file_info.completed and log_output:
            log.info(
                f"There is new {len(new_chapters)} chapters in {name}. " \
                f"Re-downloading {name}..."
            )

            # Let output list of new chapters in verbose mode only
            log.debug(f"List of new chapters = {new_chapters}")

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

# Converted formats
# cbz, cbz-volume, cbz-single, pdf, epub, etc...
class BaseConvertedFormat(BaseFormat):
    # Now, you maybe wondering. Some functions in this class want to access `self.file_ext` value.
    # But it's not declared yet in this base class. How ?
    # Well the answer is to create a new class that has `file_ext` variable
    # stored in class variables with utility functions that related to
    # file extension creation (zip, 7z, epub, pdf, etc...)
    # and use that class in each format clasess
    # See `CBZFileExt` class in `format/comic_book.py` module for example

    def __init__(self, *args, **kwargs):
        # Each formats must implement this
        # to check if optional packages is installed or not
        self.check_dependecies()

        super().__init__(*args, **kwargs)

    def add_fi(self, name, id, path, chapters=None):
        """Add new DownloadTracker._FileInfo to the tracker"""
        file_hash = create_file_hash_sha256(path)

        name = f"{name}{self.file_ext}"

        # Prevent duplicate
        self.manga.tracker.remove_file_info_from_name(name)

        self.manga.tracker.add_file_info(
            name=name,
            id=id,
            hash=file_hash,
            null_images=True,
            null_chapters=False if chapters else True
        )

        # Single chapter
        if not chapters and id is not None:
            self.mark_read_chapter(id)

        if chapters:
            for ch, _ in chapters:
                self.manga.tracker.add_chapter_info(
                    name=name,
                    chapter_name=ch.name,
                    chapter_id=ch.id
                )
                self.mark_read_chapter(ch.id)
        
        self.manga.tracker.toggle_complete(name, True)

    def check_fi_completed(self, name):
        tracker = self.manga.tracker
        fi = tracker.get(name)
        if fi is None:
            return False
        
        return fi.completed

    def download_chapters(self, worker, chapters):
        raise NotImplementedError
    
    def download_volumes(self, worker, volumes):
        raise NotImplementedError

    def download_single(self, worker, total, merged_name, chapters):
        raise NotImplementedError

class ConvertedChaptersFormat(BaseConvertedFormat):
    def main(self):
        manga = self.manga
        worker = self.create_worker()
        tracker = manga.tracker

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        # Steps for existing (downloaded) chapters:
        # - Check for new chapters.
        # - Download the new chapters (if available)
        # - Verify downloaded chapters

        # Steps for new (not downloaded) chapters:
        # - Download all of them, yes

        self.write_tachiyomi_info()

        log.info("Preparing to download...")
        cache = []
        cache.extend(manga.chapters.iter(**self.kwargs_iter))

        # There is no existing (downloaded) chapters
        # Download all of them
        if tracker.empty:
            self.download_chapters(worker, cache)

            log.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        chapters = []
        # Check for new chapters in existing (downloaded) chapters
        for chap_class, images in cache:
            chap_name = chap_class.get_simplified_name() + self.file_ext

            fi = tracker.get(chap_name)
            if fi:
                continue
                
            # There is new chapters
            chapters.append((chap_class, images))

        # If somehow there is downloaded chapters
        # and it's not in the tracker
        # it's sus, re-download them
        for chap, _ in chapters:
            chap_name = chap.get_simplified_name() + self.file_ext
            path = self.path / chap_name

            delete_file(path)

        # Download the new chapters first 
        self.download_chapters(worker, chapters)

        chapters = []

        # Verify downloaded chapters
        for chap_class, images in cache:
            chap_name = chap_class.get_simplified_name() + self.file_ext
            
            fi = tracker.get(chap_name)

            passed = verify_sha256(fi.hash, (self.path / chap_name))
            if not passed:
                log.warning(f"'{chap_name}' is missing or unverified (hash is not matching)")
                # Either missing file or hash is not matching
                chapters.append((chap_class, images))
                delete_file(self.path / chap_name)
            else:
                log.info(f"'{chap_name}' is verified and no need to re-download")
                self.mark_read_chapter(chap_class)

        if chapters:
            log.warning(
                f"Found {len(chapters)} missing or unverified chapters, " \
                f"re-downloading {len(chapters)} chapters..."
            )

        # Download missing or unverified chapters
        self.download_chapters(worker, chapters)

        # Shutdown queue-based thread process
        worker.shutdown()

        log.info("Waiting for chapter read marker to finish")
        self.cleanup()

class ConvertedVolumesFormat(BaseConvertedFormat):
    def main(self):
        manga = self.manga
        worker = self.create_worker()
        tracker = manga.tracker

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        # Steps for existing (downloaded) volumes:
        # - Check for new chapters.
        # - Re-download the volume that has new chapters (if available)
        # - Verify downloaded volumes

        # Steps for new (not downloaded) volumes:
        # - Download all of them, yes

        cache = self.get_fmt_volume_cache(manga)

        # There is not existing (downloaded) volumes
        # Download all of them
        if tracker.empty:
            self.download_volumes(worker, cache)

            log.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        volumes = {}
        # Check for new chapters in exsiting (downloaded) volumes
        for volume, chapters in cache.items():
            volume_name = self.get_volume_name(volume) + self.file_ext
            fi = tracker.get(volume_name)

            if not fi:
                # We assume this volume has not been downloaded yet
                volumes[volume] = chapters
                continue

            for chapter, _ in chapters:
                if chapter.id in fi.chapters:
                    continue

                # New chapters detected
                volumes[volume] = chapters
                break
            
        # Delete existing volumes if the volumes containing new chapters
        # because we want to re-download them
        for volume, _ in volumes.items():
            volume_name = self.get_volume_name(volume)

            path = self.path / (volume_name + self.file_ext)
            delete_file(path)
        
        # Re-download the volumes
        self.download_volumes(worker, volumes)

        volumes = {}

        # Verify downloaded volumes
        for volume, chapters in cache.items():
            volume_name = self.get_volume_name(volume) + self.file_ext
            path = self.path / volume_name

            fi = tracker.get(volume_name)

            passed = verify_sha256(fi.hash, path)
            if not passed:
                log.warning(f"'{volume_name}' is missing or unverified (hash is not matching)")
                # Either missing file or hash is not matching
                volumes[volume] = chapters
                delete_file(path)
            else:
                log.info(f"'{volume_name}' is verified and no need to re-download")
                self.mark_read_chapter(*chapters)

        if volumes:
            log.warning(
                f"Found {len(volumes)} missing or unverified volumes, " \
                f"re-downloading {len(volumes)} volumes..."
            )

        # Download missing or unverified volumes
        self.download_volumes(worker, volumes)

        # Shutdown queue-based thread process
        worker.shutdown()

        log.info("Waiting for chapter read marker to finish")
        self.cleanup()

class ConvertedSingleFormat(BaseConvertedFormat):
    def main(self):
        manga = self.manga
        worker = self.create_worker()
        tracker = self.manga.tracker
        result_cache = self.get_fmt_single_cache(manga)

        if result_cache is None:
            # The chapters is empty
            # there is nothing we can download
            worker.shutdown()

            log.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        # Steps for existing (downloaded) file (single format):
        # - Check for new chapters.
        # - Re-download the entire file (if there is new chapters)
        # - Verify downloaded file

        # Steps for new (not downloaded) file (single format):
        # - Download all of them, yes

        cache, total, merged_name = result_cache

        # There is no existing (downloaded) file
        # Download all of them
        if tracker.empty:
            self.download_single(worker, total, merged_name, cache)

            log.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        filename = merged_name + self.file_ext

        fi = tracker.get(filename)
        if not fi:
            # We assume the file has not been downloaded yet
            self.download_single(worker, total, merged_name, cache)

            log.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        chapters = []
        # Check for new chapters in existing (downloaded) file
        for chap_class, images in cache:
            if chap_class.id in fi.chapters:
                continue

            # New chapters deteceted
            chapters.append((chap_class, images))
        
        # Download the new chapters first 
        if chapters:
            delete_file(self.path / filename)
            self.download_single(worker, total, merged_name, cache)

        # Verify downloaded file
        fi = tracker.get(filename)

        passed = verify_sha256(fi.hash, (self.path / filename))
        if not passed:
            log.warning(
                f"'{filename}' is missing or unverified (hash is not matching), " \
                "re-downloading..."
            )
            delete_file(self.path / filename)
        else:
            log.info(f"'{filename}' is verified and no need to re-download")
            self.mark_read_chapter(*cache)

        # Download missing or unverified chapters
        if not passed:
            self.download_single(worker, total, merged_name, cache)

        # Shutdown queue-based thread process
        worker.shutdown()

        log.info("Waiting for chapter read marker to finish")
        self.cleanup()