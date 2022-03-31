import io
import logging
import shutil
import zipfile
import os

from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import get_mark_image, NumberWithLeadingZeros
from ..utils import create_chapter_folder
from ..downloader import ChapterPageDownloader
from ..errors import PillowNotInstalled

# Try to import Pillow module
try:
    from PIL import Image
except ImportError:
    pillow_ready = False
else:
    pillow_ready = True

path_exists = lambda x: os.path.exists(x)

log = logging.getLogger(__name__)

class ComicBookArchive(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace
        worker = self.create_worker()

        # Begin downloading
        for vol, chap_class, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
            chap = chap_class.chapter
            chap_name = chap_class.get_name()

            # Fetching chapter images
            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            chapter_path = create_chapter_folder(base_path, chap_name)

            chapter_zip_path = base_path / (chap_name + '.cbz')
            chapter_zip = zipfile.ZipFile(
                str(chapter_zip_path),
                "a" if path_exists(chapter_zip_path) else "w"
            )

            while True:
                # Fix #10
                # Some old programs wouldn't display images correctly
                total = 0
                if self.legacy_sorting:
                    for _ in images.iter():
                        total += 1
                total_str = str(total)

                error = False
                for count, (page, img_url, img_name) in enumerate(images.iter()):
                    if self.legacy_sorting:
                        count_str = str(count)
                        img_ext = os.path.splitext(img_name)[1]
                        img_name = (count_str.zfill(len(total_str)) + img_ext)

                    img_path = chapter_path / img_name

                    log.info('Downloading %s page %s' % (chap_name, page))

                    try:
                        chapter_zip.getinfo(img_name)
                    except KeyError:
                        img_exist = False
                    else:
                        img_exist = True
                    
                    if img_exist and not self.replace:
                        log.info("File exist and replace is False, cancelling download...")
                        continue

                    downloader = ChapterPageDownloader(
                        img_url,
                        img_path,
                        replace=replace
                    )
                    success = downloader.download()

                    # One of MangaDex network are having problem
                    # Fetch the new one, and start re-downloading
                    if not success:
                        log.error('One of MangaDex network are having problem, re-fetching the images...')
                        log.info('Getting %s from chapter %s' % (
                            'compressed images' if compressed_image else 'images',
                            chap
                        ))
                        error = True
                        images.fetch()
                        break
                    else:
                        # Write it to zipfile
                        wrap = lambda: chapter_zip.writestr(img_name, img_path.read_bytes())
                        
                        # KeyboardInterrupt safe
                        worker.submit(wrap)
                        
                        # And then remove it original file
                        os.remove(img_path)
                        continue
                
                if not error:
                    break
            
            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class ComicBookArchiveSingle(BaseFormat):
    def __init__(self, *args, **kwargs):
        if not pillow_ready:
            raise PillowNotInstalled("pillow is not installed")
        
        super().__init__(*args, **kwargs)

    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace
        worker = self.create_worker()
        total = 0

        # In order to add "next chapter" image mark in end of current chapter
        # We need to cache all chapters
        log.info("Preparing to download...")
        cache = []
        # Enable log cache
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for vol, chap_class, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
            # Fix #10
            # Some programs wouldn't display images correctly
            if self.legacy_sorting:
                images.fetch()

                for _ in images.iter():
                    total += 1

            item = [vol, chap_class, images]
            cache.append(item)

        count = NumberWithLeadingZeros(total)

        # Construct .cbz filename from first and last chapter
        first_chapter = cache[0][1]
        last_chapter = cache[len(cache) - 1][1]
        manga_zip_path = base_path / sanitize_filename(first_chapter.name + " - " + last_chapter.name + '.cbz')
        manga_zip = zipfile.ZipFile(
            str(manga_zip_path),
            "a" if path_exists(manga_zip_path) else "w"
        )

        start = True
        for index, (vol, chap_class, images) in enumerate(cache):
            # Group name will be placed inside the start and end of chapter images
            chap = chap_class.chapter
            chap_name = chap_class.name

            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            # If legacy_sorting is True
            # Do not fetch it again, it has already been fetched during caching process
            if not self.legacy_sorting:
                images.fetch()

            chapter_path = create_chapter_folder(base_path, chap_name)

            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    if not start:
                        img_ext = os.path.splitext(img_name)[1]
                    else:
                        img_ext = '.png'

                    if self.legacy_sorting:
                        count_str = count.get()
                    else:
                        count_str = count.get_without_zeros()

                    img_path = chapter_path / img_name

                    file = count_str + img_ext

                    if not start:
                        log.info('Downloading %s page %s' % (chap_name, page))

                    try:
                        manga_zip.getinfo(file)
                    except KeyError:
                        img_exist = False
                    else:
                        img_exist = True
                    
                    if img_exist and not self.replace:
                        if not start:
                            log.info("File exist and replace is False, cancelling download...")
                        count.increase()
                        continue

                    if not start:
                        downloader = ChapterPageDownloader(
                            img_url,
                            img_path,
                            replace=replace
                        )
                        success = downloader.download()
                    else:
                        success = True

                    # One of MangaDex network are having problem
                    # Fetch the new one, and start re-downloading
                    if not success:
                        log.error('One of MangaDex network are having problem, re-fetching the images...')
                        log.info('Getting %s from chapter %s' % (
                            'compressed images' if compressed_image else 'images',
                            chap
                        ))
                        error = True
                        images.fetch()
                        break
                    else:
                        # Write it to zipfile
                        if not start:
                            wrap = lambda: manga_zip.writestr(file, img_path.read_bytes())
                        else:
                            # Insert start of chapter image
                            def wrap():
                                start_chap_file = count_str + '.png'
                                start_chap_img = get_mark_image(chap_class, cache, index, start)
                                fp = io.BytesIO()
                                start_chap_img.save(fp, 'png')
                                manga_zip.writestr(start_chap_file, fp.getvalue())
                        
                        # KeyboardInterrupt safe
                        worker.submit(wrap)
                        
                        if not start:
                            # And then remove it original file
                            os.remove(img_path)

                        if start:
                            start = False

                        count.increase()
                        continue
                
                if not error:
                    break            

            count.increase()

            # get end of chapter image
            if self.legacy_sorting:
                mark_img_file = count.get() + '.png'
            else:
                mark_img_file = count.get_without_zeros() + '.png'
            mark_img = get_mark_image(chap_class, cache, index)
            fp = io.BytesIO()
            mark_img.save(fp, 'png')

            # Insert end of chapter image
            wrap = lambda: manga_zip.writestr(mark_img_file, fp.getvalue())
            worker.submit(wrap)

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()