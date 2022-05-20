import io
import logging
import shutil
import zipfile
import os

from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import get_mark_image, NumberWithLeadingZeros, delete_file
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
        for chap_class, images in manga.chapters.iter(**self.kwargs_iter):
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
                count = None
                if self.legacy_sorting:
                    count = NumberWithLeadingZeros(images.iter())

                error = False
                for page, img_url, img_name in images.iter():
                    if self.legacy_sorting:
                        img_ext = os.path.splitext(img_name)[1]
                        img_name = count.get() + img_ext

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

                        if self.legacy_sorting:
                            count.increase()

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
                        delete_file(img_path)

                        if self.legacy_sorting:
                            count.increase()
                        continue
                
                if not error:
                    break
            
            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class ComicBookArchiveVolume(BaseFormat):
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

            # Build volume folder name
            if chap_class.volume is not None:
                volume = f'Volume. {chap_class.volume}'
            else:
                volume = 'No Volume'

            # Create volume folder
            volume_path = create_chapter_folder(base_path, volume)

            volume_zip_path = base_path / (volume + '.cbz')
            volume_zip = zipfile.ZipFile(
                str(volume_zip_path),
                "a" if path_exists(volume_zip_path) else "w"
            )

            for chap_class, images in chapters:
                chap = chap_class.chapter
                chap_name = chap_class.get_name()

                # Insert "start of the chapter" image
                if self.legacy_sorting:
                    img_name = count.get() + '.png'
                else:
                    img_name = count.get_without_zeros() + '.png'

                # Make sure we never duplicated it
                write_start_image = False
                try:
                    volume_zip.getinfo(img_name)
                except KeyError:
                    write_start_image = True
                
                if write_start_image:
                    img = get_mark_image(chap_class)
                    fp = io.BytesIO()
                    img.save(fp, 'png')
                    job = lambda: volume_zip.writestr(img_name, fp.getvalue())
                    worker.submit(job)

                count.increase()

                # Fetching chapter images
                log.info('Getting %s from chapter %s' % (
                    'compressed images' if compressed_image else 'images',
                    chap
                ))
                images.fetch()

                while True:
                    error = False
                    for page, img_url, img_name in images.iter():
                        img_ext = os.path.splitext(img_name)[1]
                        if self.legacy_sorting:
                            img_name = count.get() + img_ext
                        else:
                            img_name = count.get_without_zeros() + img_ext

                        img_path = volume_path / img_name

                        log.info('Downloading %s page %s' % (chap_name, page))

                        try:
                            volume_zip.getinfo(img_name)
                        except KeyError:
                            img_exist = False
                        else:
                            img_exist = True
                        
                        if img_exist and not self.replace:
                            log.info("File exist and replace is False, cancelling download...")
                            count.increase()
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
                            wrap = lambda: volume_zip.writestr(img_name, img_path.read_bytes())
                            
                            # KeyboardInterrupt safe
                            worker.submit(wrap)
                            
                            # And then remove it original file
                            delete_file(img_path)

                            count.increase()
                            continue
                    
                    if not error:
                        break
                
            # Remove original chapter folder
            shutil.rmtree(volume_path, ignore_errors=True)

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
        for chap_class, images in manga.chapters.iter(**self.kwargs_iter):
            # Fix #10
            # Some programs wouldn't display images correctly
            if self.legacy_sorting:
                # Each chapters has one page that has "Chapter n"
                # This is called "start of the chapter" image
                total += 1

                total += chap_class.pages

            item = [chap_class, images]
            cache.append(item)

        count = NumberWithLeadingZeros(total)

        # Construct .cbz filename from first and last chapter
        first_chapter = cache[0][0]
        last_chapter = cache[len(cache) - 1][0]
        manga_zip_path = base_path / sanitize_filename(first_chapter.name + " - " + last_chapter.name + '.cbz')
        manga_zip = zipfile.ZipFile(
            str(manga_zip_path),
            "a" if path_exists(manga_zip_path) else "w"
        )

        for chap_class, images in cache:
            # Insert "start of the chapter" image
            if self.legacy_sorting:
                img_name = count.get() + '.png'
            else:
                img_name = count.get_without_zeros() + '.png'

            # Make sure we never duplicated it
            write_start_image = False
            try:
                manga_zip.getinfo(img_name)
            except KeyError:
                write_start_image = True
            
            if write_start_image:
                img = get_mark_image(chap_class)
                fp = io.BytesIO()
                img.save(fp, 'png')
                job = lambda: manga_zip.writestr(img_name, fp.getvalue())
                worker.submit(job)

            count.increase()

            # Group name will be placed inside the start of chapter images
            chap = chap_class.chapter
            chap_name = chap_class.name

            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            chapter_path = create_chapter_folder(base_path, chap_name)

            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    img_ext = os.path.splitext(img_name)[1]
                    if self.legacy_sorting:
                        img_name = count.get() + img_ext
                    else:
                        img_name = count.get_without_zeros() + img_ext

                    img_path = chapter_path / img_name

                    log.info('Downloading %s page %s' % (chap_name, page))

                    try:
                        manga_zip.getinfo(img_name)
                    except KeyError:
                        img_exist = False
                    else:
                        img_exist = True
                    
                    if img_exist and not self.replace:
                        log.info("File exist and replace is False, cancelling download...")
                        count.increase()
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
                        wrap = lambda: manga_zip.writestr(img_name, img_path.read_bytes())
                        
                        # KeyboardInterrupt safe
                        worker.submit(wrap)
                        
                        # And then remove it original file
                        delete_file(img_path)

                        count.increase()
                        continue
                
                if not error:
                    break            

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()