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
import shutil
import os

from .base import BaseFormat
from .utils import (
    NumberWithLeadingZeros,
    get_chapter_info,
    verify_sha256,
    create_file_hash_sha256,
    get_volume_cover,
)
from ..path.op import get_filename
from ..utils import create_directory, delete_file
from ..progress_bar import progress_bar_manager as pbm

log = logging.getLogger(__name__)


# TODO: PLEASE REFACTOR THIS CODE (Raw, RawVolume, RawSingle)
class Raw(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        data = manga.chapters.iter(**self.kwargs_iter)
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
                failed_images = []
                dir_name = get_filename(self.manga, chap_class, "", format="chapter")

                file_info = self.get_fi_chapter_fmt(dir_name, chap_class.id)
                chapter_path = create_directory(dir_name, base_path)
                ignored = self.config.ignore_missing_chapters

                if file_info is None:
                    fi_images = []
                    fi_completed = False
                else:
                    fi_images = file_info.images
                    fi_completed = file_info.completed

                for im_info in fi_images:
                    verified = verify_sha256(im_info.hash, chapter_path / im_info.name)
                    if not verified:
                        failed_images.append(im_info)

                if failed_images and fi_completed and not ignored:
                    pbm.logger.warning(
                        f"Found {len(failed_images)} unverified or missing images "
                        f"from {dir_name}. Re-downloading..."
                    )

                    # Delete unverified images
                    for im_info in failed_images:
                        im_path = chapter_path / im_info.name

                        pbm.logger.debug(
                            f"Removing unverified image '{im_path.resolve()}'"
                        )
                        delete_file(im_path)
                elif not failed_images and fi_completed and (not ignored or ignored):
                    pbm.logger.info(f"'{dir_name}' is verified. no need to re-download")
                    self.mark_read_chapter(chap_class)
                    chapters_pb.update(1)
                    continue
                elif failed_images and fi_completed and ignored:
                    pbm.logger.info(
                        f"{dir_name!r} is missing but got ignored, "
                        "since --ignore-missing-chapters is set"
                    )
                    continue

                count = NumberWithLeadingZeros(chap_class.pages)

                images = self.get_images(chap_class, images, chapter_path, count)
                if self.config.upscale:
                    try:
                        upscaler = self._get_or_create_upscaler()
                        images = upscaler.process_images(images)
                        self._cleanup_upscale_markers(images)
                    except ImportError:
                        pbm.logger.warning(
                            "Upscale dependencies are not installed. Skipping upscale.\n"
                            "Install optional deps: pip install 'mangadex-downloader[optional,upscale]'"
                        )

                data = []
                for im in images:
                    basename = os.path.basename(im)
                    im_hash = create_file_hash_sha256(im)
                    data.append((basename, im_hash, chap_class.id, dir_name))

                manga.tracker.add_images_info(data)
                manga.tracker.toggle_complete(dir_name, True)

                self.mark_read_chapter(chap_class)
                chapters_pb.update(1)

            chapters_pb.reset()
            volumes_pb.update(1)

        if not pbm.stacked:
            pbm.get_convert_pb().close()

        pbm.logger.info("Waiting for chapter read marker to finish")
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
        pbm.set_volumes_total(len(cache.keys()))
        for volume, chapters in cache.items():
            if not self.config.create_no_volume and volume is None:
                pbm.logger.debug(
                    "No volume is skipped because of --create-no-volume is not enabled"
                )
                pbm.get_volumes_pb().update(1)
                continue

            pbm.set_chapters_total(len(chapters))
            success_images = {}
            failed_images = []
            total = self.get_total_pages_for_volume_fmt(chapters)

            chapters_pb = pbm.get_chapters_pb()
            volumes_pb = pbm.get_volumes_pb()

            count = NumberWithLeadingZeros(total)

            placeholder_obj = self.create_placeholder_obj_for_volume_fmt(
                volume, chapters
            )

            volume_name = get_filename(self.manga, placeholder_obj, "", format="volume")

            volume_path = create_directory(volume_name, base_path)
            file_info = self.get_fi_volume_or_single_fmt(volume_name, volume=volume)
            new_chapters = self.get_new_chapters(file_info, chapters, volume_name)
            ignored = self.config.ignore_missing_chapters

            if file_info is None:
                fi_images = []
                fi_completed = False
            else:
                fi_images = file_info.images
                fi_completed = file_info.completed

            # Only checks if ``file_info.complete`` state is True
            if new_chapters and fi_completed:
                # Re-create directory to prevent error
                shutil.rmtree(volume_path, ignore_errors=True)
                volume_path = create_directory(volume_name, base_path)

            for im_info in fi_images:
                verified = verify_sha256(im_info.hash, volume_path / im_info.name)
                if not verified:
                    failed_images.append(im_info)

            if failed_images and fi_completed and not new_chapters and not ignored:
                pbm.logger.warning(
                    f"Found {len(failed_images)} unverified or missing images "
                    f"from {volume_name}. Re-downloading..."
                )

                # Delete unverified images
                for im_info in failed_images:
                    im_path = volume_path / im_info.name

                    pbm.logger.debug(f"Removing unverified image '{im_path.resolve()}'")
                    delete_file(im_path)
            elif not failed_images and fi_completed and (not ignored or ignored):
                pbm.logger.info(f"'{volume_name}' is verified. no need to re-download")
                self.mark_read_chapter(*chapters)
                chapters_pb.update(1)
                continue
            elif failed_images and fi_completed and ignored:
                pbm.logger.info(
                    f"{volume_name!r} is missing but got ignored, "
                    "since --ignore-missing-chapters is set"
                )
                continue

            # Create volume cover
            if self.config.use_volume_cover:
                img_name = count.get() + ".png"
                img_path = volume_path / img_name

                get_volume_cover(manga, volume, img_path, self.replace)
                count.increase()

            # Chapters that have images that are failed to verify
            # (hash is not matching)
            chapter_failed_images = set(i.chapter_id for i in failed_images)

            for chap_class, images in chapters:
                if chap_class.id not in chapter_failed_images and fi_completed:
                    count.increase(chap_class.pages)
                    continue

                img_name = count.get() + ".png"
                img_path = volume_path / img_name

                # Insert chapter info (cover) image
                if self.config.use_chapter_cover:
                    get_chapter_info(self.manga, chap_class, img_path)
                    count.increase()

                images = self.get_images(chap_class, images, volume_path, count)

                if self.config.upscale:
                    try:
                        upscaler = self._get_or_create_upscaler()
                        images = upscaler.process_images(images)
                        self._cleanup_upscale_markers(images)
                    except ImportError:
                        pbm.logger.warning(
                            "Upscale dependencies are not installed. Skipping upscale.\n"
                            "Install optional deps: pip install 'mangadex-downloader[optional,upscale]'"
                        )

                success_images[chap_class] = images

                pbm.get_pages_pb().reset()
                chapters_pb.update(1)

            chaps_data = []
            imgs_data = []
            for chap_cls, images in success_images.items():
                chaps_data.append((chap_cls.name, chap_cls.id, volume_name))

                for im in images:
                    basename = os.path.basename(im)
                    im_hash = create_file_hash_sha256(im)
                    imgs_data.append((basename, im_hash, chap_cls.id, volume_name))

            tracker.add_chapters_info(chaps_data)
            tracker.add_images_info(imgs_data)
            tracker.toggle_complete(volume_name, True)

            chapters_pb.reset()
            volumes_pb.update(1)

        pbm.logger.info("Waiting for chapter read marker to finish")
        self.cleanup()


class RawSingle(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        tracker = manga.tracker
        file_info = None
        success_images = {}
        failed_images = []

        # Recreate DownloadTracker JSON file if --replace is present
        if self.replace:
            manga.tracker.recreate()

        result_cache = self.get_fmt_single_cache(manga)

        if result_cache is None:
            # The chapters is empty
            # there is nothing we can download
            pbm.logger.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return

        cache, total = result_cache
        placeholder_obj = self.create_placeholder_obj_for_single_fmt(cache)
        name = get_filename(self.manga, placeholder_obj, "", format="single")

        count = NumberWithLeadingZeros(total)

        path = create_directory(name, base_path)
        file_info = self.get_fi_volume_or_single_fmt(name)
        new_chapters = self.get_new_chapters(file_info, cache, name)
        ignored = self.config.ignore_missing_chapters

        if file_info is None:
            fi_images = []
            fi_completed = False
        else:
            fi_images = file_info.images
            fi_completed = file_info.completed

        # Only checks if ``file_info.complete`` state is True
        if new_chapters and fi_completed:
            # Re-create directory to prevent error
            shutil.rmtree(path, ignore_errors=True)
            path = create_directory(name, base_path)

        for im_info in fi_images:
            verified = verify_sha256(im_info.hash, path / im_info.name)
            if not verified:
                failed_images.append(im_info)

        if failed_images and fi_completed and not new_chapters and not ignored:
            pbm.logger.warning(
                f"Found {len(failed_images)} unverified or missing images from {name}. "
                "Re-downloading..."
            )

            # Delete unverified images
            for im_info in failed_images:
                im_path = path / im_info.name

                pbm.logger.debug(f"Removing unverified image '{im_path.resolve()}'")
                delete_file(im_path)
        elif not failed_images and fi_completed and (not ignored or ignored):
            pbm.logger.info(f"'{name}' is verified. no need to re-download")
            self.mark_read_chapter(*cache)

            pbm.logger.info("Waiting for chapter read marker to finish")
            self.cleanup()
            return
        elif failed_images and fi_completed and ignored:
            pbm.logger.info(
                f"{name!r} is missing but got ignored, "
                "since --ignore-missing-chapters is set"
            )
            return

        # Chapters that have images that are failed to verify
        # (hash is not matching)
        chapter_failed_images = [i.chapter_id for i in failed_images]

        volumes = {}
        for chap_class, chap_images in cache:
            self.append_cache_volumes(
                volumes, chap_class.volume, (chap_class, chap_images)
            )

        pbm.set_volumes_total(len(volumes.keys()))
        for _, chapters in volumes.items():
            pbm.set_chapters_total(len(chapters))

            chapters_pb = pbm.get_chapters_pb()
            volumes_pb = pbm.get_volumes_pb()

            for chap_class, images in cache:
                if chap_class.id not in chapter_failed_images and fi_completed:
                    count.increase(chap_class.pages)
                    chapters_pb.update(1)
                    continue

                # Insert chapter info (cover) image
                img_name = count.get() + ".png"
                img_path = path / img_name

                if self.config.use_chapter_cover:
                    get_chapter_info(self.manga, chap_class, img_path)
                    count.increase()

                images = self.get_images(chap_class, images, path, count)

                if self.config.upscale:
                    try:
                        upscaler = self._get_or_create_upscaler()
                        images = upscaler.process_images(images)
                        self._cleanup_upscale_markers(images)
                    except ImportError:
                        pbm.logger.warning(
                            "Upscale dependencies are not installed. Skipping upscale.\n"
                            "Install optional deps: pip install 'mangadex-downloader[optional,upscale]'"
                        )

                success_images[chap_class] = images

                self.mark_read_chapter(chap_class)

                pbm.get_pages_pb().reset()
                chapters_pb.update(1)

            chapters_pb.reset()
            volumes_pb.update(1)

        chaps_data = []
        imgs_data = []
        for chap_cls, images in success_images.items():
            chaps_data.append((chap_cls.name, chap_cls.id, name))

            for im in images:
                basename = os.path.basename(im)
                im_hash = create_file_hash_sha256(im)
                imgs_data.append((basename, im_hash, chap_cls.id, name))

        tracker.add_chapters_info(chaps_data)
        tracker.add_images_info(imgs_data)
        tracker.toggle_complete(name, True)

        pbm.logger.info("Waiting for chapter read marker to finish")
        self.cleanup()
