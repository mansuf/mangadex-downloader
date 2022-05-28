import io
import logging
import shutil
import os

from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import get_mark_image, NumberWithLeadingZeros, delete_file, verify_sha256
from ..utils import create_chapter_folder
from ..downloader import ChapterPageDownloader
from ..errors import MangaDexException

try:
    import py7zr
except ImportError:
    PY7ZR_OK = False
else:
    PY7ZR_OK = True

class py7zrNotInstalled(MangaDexException):
    """Raised when py7zr is not installed"""
    pass

log = logging.getLogger(__name__)

class SevenZip(BaseFormat):
    def __init__(self, *args, **kwargs):
        if not PY7ZR_OK:
            raise py7zrNotInstalled("py7zr is not installed")

        super().__init__(*args, **kwargs)

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

            chapter_zip_path = base_path / (chap_name + '.cb7')
            if chapter_zip_path.exists() and replace:
                delete_file(chapter_zip_path)

            while True:
                # Fix #10
                # Some old programs wouldn't display images correctly
                count = NumberWithLeadingZeros(images.iter())

                error = False
                for page, img_url, img_name in images.iter():
                    server_file = img_name

                    img_ext = os.path.splitext(img_name)[1]
                    img_name = count.get() + img_ext

                    img_path = chapter_path / img_name

                    log.info('Downloading %s page %s' % (chap_name, page))

                    verified = None
                    if chapter_zip_path.exists():
                        with py7zr.SevenZipFile(chapter_zip_path, 'r') as chapter_zip:
                            fp_files = chapter_zip.read([img_name])

                            for _, fp in fp_files.items():
                                # Verify file
                                if self.verify and not replace:
                                    # Can be True, False, or None
                                    content = fp.read()
                                    verified = verify_sha256(server_file, data=content)
                                elif not self.verify:
                                    verified = None
                                else:
                                    verified = False

                    # If file still in intact and same as the server
                    # Continue to download the others
                    if verified:
                        log.info("File exist and same as file from MangaDex server, cancelling download...")
                        count.increase()
                        continue
                    elif verified == False and not self.replace:
                        # File is not same server, probably modified
                        log.info("File exist and NOT same as file from MangaDex server, re-downloading...")
                        replace = True

                    downloader = ChapterPageDownloader(
                        img_url,
                        img_path,
                        replace=replace
                    )
                    success = downloader.download()

                    if verified == False and not self.replace:
                        replace = self.replace

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
                        def wrap():
                            args = (
                                chapter_zip_path,
                                "a" if os.path.exists(chapter_zip_path) else "w"
                            )

                            with py7zr.SevenZipFile(*args) as chapter_zip:
                                chapter_zip.write(img_path, img_name)

                            # And then remove it original file
                            delete_file(img_path)

                        # KeyboardInterrupt safe
                        worker.submit(wrap)

                        count.increase()
                        continue
                
                if not error:
                    break
            
            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class SevenZipVolume(SevenZip):
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

            volume_zip_path = base_path / (volume + '.cb7')
            if volume_zip_path.exists() and replace:
                delete_file(volume_zip_path)

            def write_image(img_path, img_name):
                args = (
                    volume_zip_path,
                    "a" if os.path.exists(volume_zip_path) else "w",
                )

                with py7zr.SevenZipFile(*args) as volume_zip:
                    volume_zip.write(img_path, img_name)

                delete_file(img_path)

            for chap_class, images in chapters:
                chap = chap_class.chapter
                chap_name = chap_class.get_name()

                # Insert "start of the chapter" image
                img_name = count.get() + '.png'

                # Make sure we never duplicated it
                write_start_image = True
                if volume_zip_path.exists():
                    with py7zr.SevenZipFile(volume_zip_path, 'r') as volume_zip:
                        write_start_image = img_name not in volume_zip.getnames()

                if write_start_image:
                    img = get_mark_image(chap_class)
                    img_path = volume_path / img_name
                    img.save(img_path, 'png')
                    worker.submit(lambda: write_image(img_path, img_name))

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
                        server_file = img_name

                        img_ext = os.path.splitext(img_name)[1]
                        img_name = count.get() + img_ext

                        img_path = volume_path / img_name

                        log.info('Downloading %s page %s' % (chap_name, page))

                        verified = None
                        if volume_zip_path.exists():
                            with py7zr.SevenZipFile(volume_zip_path, 'r') as volume_zip:
                                fp_files = volume_zip.read([img_name])

                                for _, fp in fp_files.items():
                                    # Verify file
                                    if self.verify and not replace:
                                        # Can be True, False, or None
                                        content = fp.read()
                                        verified = verify_sha256(server_file, data=content)
                                    elif not self.verify:
                                        verified = None
                                    else:
                                        verified = False

                        # If file still in intact and same as the server
                        # Continue to download the others
                        if verified:
                            log.info("File exist and same as file from MangaDex server, cancelling download...")
                            count.increase()
                            continue
                        elif verified == False and not self.replace:
                            # File is not same server, probably modified
                            log.info("File exist and NOT same as file from MangaDex server, re-downloading...")
                            replace = True

                        downloader = ChapterPageDownloader(
                            img_url,
                            img_path,
                            replace=replace
                        )
                        success = downloader.download()

                        if verified == False and not self.replace:
                            replace = self.replace

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
                            wrap = lambda: write_image(img_path, img_name)
                            
                            # KeyboardInterrupt safe
                            worker.submit(wrap)
                            
                            count.increase()
                            continue
                    
                    if not error:
                        break
                
            # Remove original chapter folder
            shutil.rmtree(volume_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class SevenZipSingle(SevenZip):
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
        manga_zip_path = base_path / sanitize_filename(first_chapter.name + " - " + last_chapter.name + '.cb7')
        if manga_zip_path.exists() and replace:
            delete_file(manga_zip_path)

        def write_image(img_path, img_name):
            args = (
                manga_zip_path,
                "a" if os.path.exists(manga_zip_path) else "w",
            )

            with py7zr.SevenZipFile(*args) as manga_zip:
                manga_zip.write(img_path, img_name)

            delete_file(img_path)

        for chap_class, images in cache:
            # Group name will be placed inside the start of chapter images
            chap = chap_class.chapter
            chap_name = chap_class.name

            chapter_path = create_chapter_folder(base_path, chap_name)

            # Insert "start of the chapter" image
            img_name = count.get() + '.png'

            # Make sure we never duplicated it
            write_start_image = True
            if manga_zip_path.exists():
                with py7zr.SevenZipFile(manga_zip_path, 'r') as manga_zip:
                    write_start_image = img_name not in manga_zip.getnames()

            if write_start_image:
                img = get_mark_image(chap_class)
                img_path = chapter_path / img_name
                img.save(img_path, 'png')
                worker.submit(lambda: write_image(img_path, img_name))

            count.increase()

            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    server_file = img_name

                    img_ext = os.path.splitext(img_name)[1]
                    img_name = count.get() + img_ext

                    img_path = chapter_path / img_name

                    log.info('Downloading %s page %s' % (chap_name, page))

                    verified = None
                    if manga_zip_path.exists():
                        with py7zr.SevenZipFile(manga_zip_path, 'r') as manga_zip:
                            fp_files = manga_zip.read([img_name])

                            for _, fp in fp_files.items():
                                # Verify file
                                if self.verify and not replace:
                                    # Can be True, False, or None
                                    content = fp.read()
                                    verified = verify_sha256(server_file, data=content)
                                elif not self.verify:
                                    verified = None
                                else:
                                    verified = False

                    # If file still in intact and same as the server
                    # Continue to download the others
                    if verified:
                        log.info("File exist and same as file from MangaDex server, cancelling download...")
                        count.increase()
                        continue
                    elif verified == False and not self.replace:
                        # File is not same server, probably modified
                        log.info("File exist and NOT same as file from MangaDex server, re-downloading...")
                        replace = True

                    downloader = ChapterPageDownloader(
                        img_url,
                        img_path,
                        replace=replace
                    )
                    success = downloader.download()

                    if verified == False and not self.replace:
                        replace = self.replace

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
                        wrap = lambda: write_image(img_path, img_name)
                        
                        # KeyboardInterrupt safe
                        worker.submit(wrap)
                        
                        count.increase()
                        continue
                
                if not error:
                    break            

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()