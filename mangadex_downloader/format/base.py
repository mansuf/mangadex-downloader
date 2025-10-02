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
import shutil
from .utils import (
    NumberWithLeadingZeros,
    verify_sha256,
    get_md_file_hash,
    create_file_hash_sha256,
    QueueWorkerReadMarker,
)
from .placeholders import VolumePlaceholder, SingleChaptersPlaceholder
from ..downloader import ChapterPageDownloader
from ..utils import QueueWorker, create_directory, delete_file
from ..progress_bar import progress_bar_manager as pbm
from ..path.op import get_filename

log = logging.getLogger(__name__)


class BaseFormat:
    def __init__(
        self,
        path,
        manga,
        replace,
        kwargs_iter_chapter_img,
        splitted_format=False,
        _internal_create_no_volume=False,
    ):
        # "Circular imports" problem
        from ..config import config

        self.config = config
        self.path = path
        self.manga = manga
        self.compress_img = config.use_compressed_image
        self.replace = replace
        self.kwargs_iter = kwargs_iter_chapter_img

        self.splitted_format = splitted_format
        self._internal_vars = {"create_no_volume": _internal_create_no_volume}

        self.chapter_read_marker = QueueWorkerReadMarker(manga.id)

        # Only start worker for chapter read marker
        # if user is logged in and --download-mode is set to unread
        if (
            self.config.download_mode == "unread"
            and self.chapter_read_marker.net.mangadex.check_login()
        ):
            self.chapter_read_marker.start()

        self.worker = None

        if config.progress_bar_layout == "stacked":
            pbm.stacked = True

    def cleanup(self):
        # Shutdown some worker threads
        self.chapter_read_marker.shutdown(blocking=True)

        if self.worker:
            self.worker.shutdown(blocking=True)

        if pbm.stacked:
            pbm.close_all()
            pbm.stacked = False

    def get_images(self, chap_class, images, path, count):
        imgs = []
        chap = chap_class.chapter
        chap_name = chap_class.get_name()

        # Fetching chapter images
        pbm.logger.info(
            "Getting %s from chapter %s"
            % ("compressed images" if self.compress_img else "images", chap)
        )
        images.fetch()

        total = sum(1 for _ in images.iter())

        pbm.set_pages_total(total)
        pages_pb = pbm.get_pages_pb()

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
                    pbm.logger.debug(
                        f"Page {page} ({img_name}) exists and is verified, "
                        "cancelling download..."
                    )
                    count.increase()
                    imgs.append(img_path)
                    pages_pb.update(1)
                    continue
                elif verified is False and not self.replace:
                    # File is not same server, probably modified
                    pbm.logger.warning(
                        f"Page {page} ({img_name}) exists but "
                        "failed to verify (hash is not matching), re-downloading..."
                    )

                pbm.logger.info("Downloading %s page %s" % (chap_name, page))

                downloader = ChapterPageDownloader(
                    img_url,
                    img_path,
                    replace=replace,
                )
                success = downloader.download()
                downloader.cleanup()

                # One of MangaDex network are having problem
                # Fetch the new one, and start re-downloading
                if not success:
                    pbm.logger.error(
                        "One of MangaDex network is failing, re-fetching the images..."
                    )
                    pbm.logger.info(
                        "Getting %s from chapter %s"
                        % ("compressed images" if self.compress_img else "images", chap)
                    )
                    error = True
                    images.fetch()
                    pages_pb.reset()
                    break
                else:
                    imgs.append(img_path)
                    count.increase()
                    pages_pb.update(1)
                    continue

            if not error:
                return imgs

    def mark_read_chapter(self, *chapters):
        """Mark a chapter as read"""
        if (
            self.config.download_mode == "unread"
            and self.chapter_read_marker.net.mangadex.check_login()
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
        kwargs_iter["log_cache"] = True
        for chap_class, chap_images in manga.chapters.iter(**self.kwargs_iter):
            total += chap_class.pages

            item = [chap_class, chap_images]
            cache.append(item)

        if not cache:
            return None

        if self.config.use_chapter_cover:
            total += len(cache)

        return cache, total

    def get_total_pages_for_volume_fmt(self, chapters):
        total = 0

        if self.config.use_volume_cover:
            total += 1

        if self.config.use_chapter_cover:
            total += len(chapters)

        for chap_class, _ in chapters:
            total += chap_class.pages

        return total

    def append_cache_volumes(self, cache, volume, item):
        try:
            data = cache[volume]
        except KeyError:
            cache[volume] = [item]
        else:
            data.append(item)

    def get_fmt_volume_cache(self, manga):
        """Get all cached volumes"""
        # Sorting volumes
        log.info("Preparing to download")
        cache = {}
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter["log_cache"] = True
        for chap_class, chap_images in manga.chapters.iter(**kwargs_iter):
            self.append_cache_volumes(
                cache, chap_class.volume, [chap_class, chap_images]
            )

        return cache

    def get_volume_name(self, vol):
        # Build volume folder name
        if vol is not None:
            name = f"Vol. {vol}"
        else:
            name = "No Volume"

        return name

    def get_fi_chapter_fmt(self, name, id, hash=None):
        """Get DownloadTracker._FileInfo for chapter format (raw, cbz, epub, etc..)

        Create one if it doesn't exist
        """
        tracker = self.manga.tracker
        file_info = tracker.get(name)
        if file_info is None:
            tracker.init_write_mode()
            tracker.add_file_info(
                name=name,
                manga_id=self.manga.id,
                ch_id=None,
                hash=hash,
            )
            file_info = tracker.get(name)

        return file_info

    def get_fi_volume_or_single_fmt(self, name, hash=None, volume=None):
        """Get DownloadTracker._FileInfo for volume or single format

        Create one if it doesn't exist
        """
        tracker = self.manga.tracker
        file_info = tracker.get(name)
        if file_info is None:
            tracker.init_write_mode()
            tracker.add_file_info(
                name=name, manga_id=self.manga.id, ch_id=None, hash=hash, volume=volume
            )
            file_info = tracker.get(name)

        return file_info

    def get_new_chapters(self, file_info, chapters, name, log_output=True):
        """Retrieve new chapters for volume and single formats"""
        if file_info is None:
            fi_chapters = []
            fi_completed = False
        else:
            fi_chapters = file_info.chapters
            fi_completed = file_info.completed

        # Check for new chapters in volume
        new_chapters = []
        for chap_class, _ in chapters:
            if chap_class.id not in fi_chapters:
                new_chapters.append(chap_class.name)

        if new_chapters and fi_completed and log_output:
            log.info(
                f"There is new {len(new_chapters)} chapters in {name}. "
                f"Re-downloading {name}..."
            )

            # Let output list of new chapters in verbose mode only
            log.debug(f"List of new chapters = {new_chapters}")

        return new_chapters

    def create_placeholder_obj_for_volume_fmt(self, volume, chapters):
        chapters = [c for c, _ in chapters]

        placeholder_obj = VolumePlaceholder(volume)
        placeholder_obj.chapters.extend(chapters)
        placeholder_obj.chapters.first = chapters[0]
        placeholder_obj.chapters.last = chapters[-1]

        return placeholder_obj

    def create_placeholder_obj_for_single_fmt(self, chapters):
        chapters = [c for c, _ in chapters]

        placeholder_obj = SingleChaptersPlaceholder(chapters)
        placeholder_obj.first = chapters[0]
        placeholder_obj.last = chapters[-1]

        return placeholder_obj

    def create_worker(self):
        # If CTRL+C is pressed all process is interrupted, right ?
        # Now when this happens in PDF or ZIP processing, this can cause
        # corrupted files.
        # The purpose of this function is to prevent interrupt from CTRL+C
        # Let the job done safely and then shutdown gracefully
        self.worker = QueueWorker()
        self.worker.start()

    def main(self):
        """Execute main format

        Subclasses must implement this.
        """
        raise NotImplementedError


# Converted formats
# cbz, cbz-volume, cbz-single, pdf, epub, etc...
class BaseConvertedFormat(BaseFormat):
    # Now, you maybe wondering.
    # Some functions in this class want to access `self.file_ext` value.
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

        self.total_volumes = 0
        self.total_chapters_per_volume = 0

        super().__init__(*args, **kwargs)

    def add_fi(self, name, id, path, chapters=None, volume=None):
        file_hash = create_file_hash_sha256(path)

        # Prevent duplicate
        self.manga.tracker.remove_file_info_from_name(name)

        self.manga.tracker.add_file_info(
            name=name, manga_id=self.manga.id, ch_id=id, hash=file_hash, volume=volume
        )

        # Single chapter
        if not chapters and id is not None:
            self.mark_read_chapter(id)

        if chapters:
            chaps_data = [(ch.name, ch.id, name) for ch, _ in chapters]
            self.manga.tracker.add_chapters_info(chaps_data)
            self.mark_read_chapter(chapters)

        self.manga.tracker.toggle_complete(name, True)

    def check_fi_completed(self, name):
        if self.manga.tracker.disabled:
            return True

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
    def on_prepare(self, file_path, chapter, images):
        """This function is called after creating a directory to store downloaded images"""
        pass

    def on_finish(self, file_path, chapter, images):
        """ "This function is called after download is finished"""
        pass

    def download_chapters(self, data):
        self.manga.tracker.init_write_mode()
        volumes = {}
        for chap_class, images in data:
            self.append_cache_volumes(volumes, chap_class.volume, (chap_class, images))

        pbm.set_volumes_total(len(volumes.keys()))
        # Begin downloading
        for volume, chapters in volumes.items():

            # This means we will only download chapters that has no volume
            if (
                volume is not None
                and self.splitted_format
                and not self._internal_vars["create_no_volume"]
            ):
                continue

            pbm.set_chapters_total(len(chapters))

            chapters_pb = pbm.get_chapters_pb()
            volumes_pb = pbm.get_volumes_pb()

            for index, (chap_class, images) in enumerate(chapters, start=1):
                chap_name = chap_class.get_simplified_name()

                filename = get_filename(
                    self.manga, chap_class, self.file_ext, format="chapter"
                )
                file_path = self.path / filename

                # Check if file is exist or not
                if file_path.exists():
                    if self.replace:
                        delete_file(file_path)
                    elif self.check_fi_completed(filename):
                        pbm.logger.info(
                            f"{file_path.name!r} already exists, cancelling download..."
                        )

                        # Store file_info tracker for existing chapter
                        self.add_fi(filename, chap_class.id, file_path)

                        chapters_pb.update(1)
                        continue

                chapter_path = create_directory(chap_name, self.path)

                self.on_prepare(file_path, chap_class, images)

                count = NumberWithLeadingZeros(chap_class.pages)
                images = self.get_images(chap_class, images, chapter_path, count)
                pbm.get_pages_pb().reset()

                if self.config.upscale:
                    from ..network import Net
                    if hasattr(Net.mangadex, '_worker_report'):
                        Net.mangadex._worker_report.wait()

                    try:
                        from ..upscale import Upscaler
                        upscaler = Upscaler(self.config.upscale_scale, self.config.upscale_concurrency)
                        images = upscaler.process_images(images)
                    except ImportError:
                        pbm.logger.warning(
                            "Upscale dependencies are not installed. Skipping upscale.\n"
                            "Install optional deps: pip install 'mangadex-downloader[optional]'"
                        )

                chapters_pb.update(1)

                pbm.logger.info(
                    f"{chap_name} has finished download, converting to {self.file_ext} file..."
                )
                self.on_finish(file_path, chap_class, images)

                if index != len(chapters) and pbm.stacked:
                    pbm.get_convert_pb().reset()
                elif not pbm.stacked:
                    pbm.get_convert_pb().close()

                # Remove original chapter folder
                shutil.rmtree(chapter_path, ignore_errors=True)

                self.add_fi(filename, chap_class.id, file_path)

            chapters_pb.reset()
            volumes_pb.update(1)

    def main(self):
        self.create_worker()

        manga = self.manga
        tracker = manga.tracker

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace and not self.splitted_format:
            manga.tracker.recreate()

        # Steps for existing (downloaded) chapters:
        # - Check for new chapters.
        # - Download the new chapters (if available)
        # - Verify downloaded chapters

        # Steps for new (not downloaded) chapters:
        # - Download all of them, yes

        log.info("Preparing to download...")
        cache = []
        cache.extend(manga.chapters.iter(**self.kwargs_iter))

        # There is no existing (downloaded) chapters
        # Download all of them
        if tracker.disabled or tracker.empty:
            self.download_chapters(cache)

            pbm.logger.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        files_info = tracker.get_all_files_info()

        chapters = []
        existing_chapter_ids = [i.ch_id for i in files_info]
        # Check for new chapters in existing (downloaded) chapters
        for chap_class, images in cache:
            if chap_class.id in existing_chapter_ids:
                continue

            # There is new chapters
            chapters.append((chap_class, images))

        if chapters:
            pbm.logger.info(f"Found {len(chapters)} new chapter(s), downloading...")

            # Download the new chapters first
            self.download_chapters(chapters)

        chapters = []
        files_info = tracker.get_all_files_info()

        # Verify downloaded chapters
        pbm.logger.info("Verifying downloaded chapters...")
        for chap_class, images in cache:
            filename = get_filename(manga, chap_class, self.file_ext, format="chapter")

            for file_info in files_info:
                if filename != file_info.name:
                    continue

                ignored = self.config.ignore_missing_chapters
                passed = verify_sha256(file_info.hash, (self.path / file_info.name))
                if not ignored and not passed:
                    pbm.logger.warning(
                        f"{file_info.name!r} is missing or unverified (hash is not matching)"
                    )
                    # Either missing file or hash is not matching
                    chapters.append((chap_class, images))
                    delete_file(self.path / file_info.name)
                elif passed:
                    pbm.logger.info(
                        f"{file_info.name!r} is verified and no need to re-download"
                    )
                    self.mark_read_chapter(chap_class)
                elif ignored and not passed:
                    pbm.logger.info(
                        f"{file_info.name!r} is missing but got ignored, "
                        "since --ignore-missing-chapters is set"
                    )

        if chapters:
            pbm.logger.warning(
                f"Found {len(chapters)} missing or unverified chapters, "
                f"re-downloading {len(chapters)} chapters..."
            )

            # Download missing or unverified chapters
            self.download_chapters(chapters)

        pbm.logger.info("Waiting for chapter read marker to finish")
        self.cleanup()


class ConvertedVolumesFormat(BaseConvertedFormat):
    def on_prepare(self, file_path, volume, count):
        """This function is called after creating a directory to store downloaded images"""
        pass

    def on_iter_chapter(self, file_path, chapter, count):
        """This function is called when iterating chapters"""
        pass

    def on_received_images(self, file_path, chapter, images):
        """This function is called when format has successfully received images"""
        pass

    def on_convert(self, file_path, volume, images):
        """ "This function is called when convert process is starting"""
        pass

    def download_volumes(self, volumes):
        # Begin downloading
        self.manga.tracker.init_write_mode()
        pbm.set_volumes_total(len(volumes))

        for volume, chapters in volumes.items():
            if not self.config.create_no_volume and volume is None:
                pbm.logger.debug(
                    "No volume is skipped because of --create-no-volume is not enabled"
                )
                pbm.get_volumes_pb().update(1)
                continue

            pbm.set_chapters_total(len(chapters))
            total = self.get_total_pages_for_volume_fmt(chapters)
            images = []

            chapters_pb = pbm.get_chapters_pb()
            volumes_pb = pbm.get_volumes_pb()

            count = NumberWithLeadingZeros(total)

            # Preparing placeholders
            placeholder_obj = self.create_placeholder_obj_for_volume_fmt(
                volume, chapters
            )

            volume_name = self.get_volume_name(volume)
            filename = get_filename(
                self.manga, placeholder_obj, self.file_ext, format="volume"
            )
            file_path = self.path / filename

            # Check if exist or not
            if file_path.exists():
                if self.replace:
                    delete_file(file_path)
                elif self.check_fi_completed(filename):
                    pbm.logger.info(
                        f"{file_path.name!r} is exist and replace is False, "
                        "cancelling download..."
                    )

                    # Store file_info tracker for existing volume
                    self.add_fi(filename, None, file_path, chapters, volume)
                    continue

            # Create volume folder
            volume_path = create_directory(volume_name, self.path)

            self.on_prepare(file_path, volume, count)

            for chap_class, chap_images in chapters:
                self.on_iter_chapter(file_path, chap_class, count)

                ims = self.get_images(chap_class, chap_images, volume_path, count)

                if self.config.upscale:
                    from ..network import Net
                    if hasattr(Net.mangadex, '_worker_report'):
                        Net.mangadex._worker_report.wait()

                    try:
                        from ..upscale import Upscaler
                        upscaler = Upscaler(self.config.upscale_scale, self.config.upscale_concurrency)
                        ims = upscaler.process_images(ims)
                    except ImportError:
                        pbm.logger.warning(
                            "Upscale dependencies are not installed. Skipping upscale.\n"
                            "Install optional deps: pip install 'mangadex-downloader[optional]'"
                        )

                images.extend(ims)

                self.on_received_images(file_path, chap_class, ims)
                chapters_pb.update(1)
                pbm.get_pages_pb().reset()

            chapters_pb.reset()
            pbm.logger.info(
                f"{volume_name} has finished download, converting chapters to {self.file_ext} file..."
            )
            self.on_convert(file_path, volume, images)

            # Remove original chapter folder
            shutil.rmtree(volume_path, ignore_errors=True)

            self.add_fi(filename, None, file_path, chapters, volume)
            volumes_pb.update(1)

        if pbm.stacked:
            pbm.get_convert_pb().reset()
        else:
            pbm.get_convert_pb().close()

    def main(self):
        self.create_worker()

        manga = self.manga
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
        if tracker.disabled or tracker.empty:
            self.download_volumes(cache)

            pbm.logger.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        volumes = {}
        new_volumes_files_info = []
        # Check for new chapters in existing (downloaded) volumes
        for volume, chapters in cache.items():
            file_info = tracker.get_file_info_from_volume(volume)

            if file_info is None:
                # This mean the volume is not downloaded yet
                volumes[volume] = chapters
                continue

            for chapter, _ in chapters:
                exist_chapter_ids = [i.id for i in file_info.chapters]

                if chapter.id in exist_chapter_ids:
                    continue

                # New chapters detected
                volumes[volume] = chapters
                new_volumes_files_info.append(file_info)

                break

        # Delete existing volumes if the volumes containing new chapters
        # because we want to re-download them
        for file_info in new_volumes_files_info:
            path = self.path / file_info.name
            delete_file(path)

        # Re-download the volumes
        if volumes:
            self.download_volumes(volumes)

        volumes = {}
        files_info = tracker.get_all_files_info()

        # Verify downloaded volumes
        for volume, chapters in cache.items():
            placeholder_obj = self.create_placeholder_obj_for_volume_fmt(
                volume, chapters
            )
            filename = get_filename(
                self.manga, placeholder_obj, self.file_ext, format="volume"
            )

            for file_info in files_info:
                if filename != file_info.name:
                    continue

                path = self.path / file_info.name
                passed = verify_sha256(file_info.hash, path)
                ignored = self.config.ignore_missing_chapters
                if not ignored and not passed:
                    pbm.logger.warning(
                        f"{filename!r} is missing or unverified (hash is not matching)"
                    )
                    # Either missing file or hash is not matching
                    volumes[volume] = chapters
                    delete_file(path)
                elif passed:
                    pbm.logger.info(
                        f"{filename!r} is verified and no need to re-download"
                    )
                    self.mark_read_chapter(*chapters)
                elif ignored and not passed:
                    pbm.logger.info(
                        f"{file_info.name!r} is missing but got ignored, "
                        "since --ignore-missing-chapters is set"
                    )

        if volumes:
            pbm.logger.warning(
                f"Found {len(volumes)} missing or unverified volumes, "
                f"re-downloading {len(volumes)} volumes..."
            )

            # Download missing or unverified volumes
            self.download_volumes(volumes)

        pbm.logger.info("Waiting for chapter read marker to finish")
        self.cleanup()


class ConvertedSingleFormat(BaseConvertedFormat):
    def on_prepare(self, file_path, base_path):
        pass

    def on_iter_chapter(self, file_path, chapter, count):
        """This function is called when iterating chapters"""
        pass

    def on_received_images(self, file_path, chapter, images):
        """This function is called when format has successfully received images"""
        pass

    def on_finish(self, file_path, images):
        pass

    def download_single(self, total, data):
        images = []
        count = NumberWithLeadingZeros(total)
        self.manga.tracker.init_write_mode()

        # Preparing placeholder
        placeholder_obj = self.create_placeholder_obj_for_single_fmt(data)

        filename = get_filename(
            self.manga, placeholder_obj, self.file_ext, format="single"
        )
        file_path = self.path / filename

        # Check if exist or not
        if file_path.exists():
            if self.replace:
                delete_file(file_path)
            elif self.check_fi_completed(filename):
                pbm.logger.info(
                    f"{file_path.name!r} already exists, cancelling download..."
                )

                # Store file_info tracker for existing manga
                self.add_fi(filename, None, file_path, data)
                return

        path = create_directory(os.path.splitext(filename)[0], self.path)

        self.on_prepare(file_path, path)

        volumes = {}
        for chap_class, chap_images in data:
            self.append_cache_volumes(
                volumes, chap_class.volume, (chap_class, chap_images)
            )

        pbm.set_volumes_total(len(volumes.keys()))
        # Begin downloading
        for _, chapters in volumes.items():
            pbm.set_chapters_total(len(chapters))

            chapters_pb = pbm.get_chapters_pb()
            volumes_pb = pbm.get_volumes_pb()

            for chap_class, chap_images in chapters:
                self.on_iter_chapter(file_path, chap_class, count)

                ims = self.get_images(chap_class, chap_images, path, count)

                if self.config.upscale:
                    from ..network import Net
                    if hasattr(Net.mangadex, '_worker_report'):
                        Net.mangadex._worker_report.wait()

                    try:
                        from ..upscale import Upscaler
                        upscaler = Upscaler(self.config.upscale_scale, self.config.upscale_concurrency)
                        ims = upscaler.process_images(ims)
                    except ImportError:
                        pbm.logger.warning(
                            "Upscale dependencies are not installed. Skipping upscale.\n"
                            "Install optional deps: pip install 'mangadex-downloader[optional]'"
                        )

                self.on_received_images(file_path, chap_class, ims)
                images.extend(ims)

                chapters_pb.update(1)
                pbm.get_pages_pb().reset()

            chapters_pb.reset()
            volumes_pb.update(1)

        pbm.logger.info(
            f"Manga {self.manga.title!r} has finished download, converting chapters to {self.file_ext} file..."
        )
        self.on_finish(file_path, images)
        pbm.get_convert_pb().close()

        # Remove downloaded images
        shutil.rmtree(path, ignore_errors=True)

        self.add_fi(filename, None, file_path, data)

    def main(self):
        manga = self.manga
        tracker = self.manga.tracker
        result_cache = self.get_fmt_single_cache(manga)
        self.create_worker()

        if result_cache is None:
            # The chapters is empty
            # there is nothing we can download
            pbm.logger.info("Waiting for chapter read marker to finish")
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

        cache, total = result_cache

        # There is no existing (downloaded) file
        # Download all of them
        if tracker.disabled or tracker.empty:
            self.download_single(total, cache)

            pbm.logger.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        file_info = tracker.get_all_files_info()
        placeholder_obj = self.create_placeholder_obj_for_single_fmt(cache)
        filename = get_filename(
            self.manga, placeholder_obj, self.file_ext, format="single"
        )
        file_info = tracker.get(filename)
        chapters = []
        # Check for new chapters in existing (downloaded) file
        for chap_class, images in cache:
            if chap_class.id in file_info.chapters:
                continue

            # New chapters deteceted
            chapters.append((chap_class, images))

        # Download the new chapters first
        if chapters:
            delete_file(self.path / filename)
            self.download_single(total, cache)

        # Verify downloaded file
        file_info = tracker.get(filename)

        ignored = self.config.ignore_missing_chapters
        passed = verify_sha256(file_info.hash, (self.path / filename))
        if not ignored and not passed:
            pbm.logger.warning(
                f"{filename!r} is missing or unverified (hash is not matching), "
                "re-downloading..."
            )
            delete_file(self.path / filename)
        elif passed:
            pbm.logger.info(f"{filename!r} is verified and no need to re-download")
            self.mark_read_chapter(*cache)
        elif ignored and not passed:
            pbm.logger.info(
                f"{file_info.name!r} is missing but got ignored, "
                "since --ignore-missing-chapters is set"
            )

        # Download missing or unverified chapters
        if not passed and not ignored:
            self.download_single(total, cache)

        pbm.logger.info("Waiting for chapter read marker to finish")
        self.cleanup()
