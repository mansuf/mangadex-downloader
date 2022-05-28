import io
import logging
import os
import zipfile
from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import NumberWithLeadingZeros, get_mark_image, verify_sha256
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

class Raw(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace

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

                    # Verify file
                    if self.verify and not replace:
                        # Can be True, False, or None
                        verified = verify_sha256(server_file, img_path)
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
                        count.increase()
                        continue
                
                if not error:
                    break

class RawVolume(BaseFormat):
    def __init__(self, *args, **kwargs):
        if not pillow_ready:
            raise PillowNotInstalled("pillow is not installed")
        
        super().__init__(*args, **kwargs)

    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace

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

            for chap_class, images in chapters:
                chap = chap_class.chapter
                chap_name = chap_class.get_name()

                # Build volume folder name
                if chap_class.volume is not None:
                    volume = f'Volume. {chap_class.volume}'
                else:
                    volume = 'No Volume'

                # Fetching chapter images
                log.info('Getting %s from chapter %s' % (
                    'compressed images' if compressed_image else 'images',
                    chap
                ))
                images.fetch()

                chapter_path = create_chapter_folder(base_path, volume)

                # Insert "start of the chapter" image
                img_name = count.get() + '.png'
                img_path = chapter_path / img_name
                img = get_mark_image(chap_class)
                img.save(img_path, 'png')

                count.increase()

                while True:
                    error = False
                    for page, img_url, img_name in images.iter():
                        server_file = img_name

                        img_ext = os.path.splitext(img_name)[1]
                        img_name = count.get() + img_ext

                        img_path = chapter_path / img_name

                        log.info('Downloading %s page %s' % (chap_name, page))
    
                        # Verify file
                        if self.verify and not replace:
                            # Can be True, False, or None
                            verified = verify_sha256(server_file, img_path)
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
                            count.increase()
                            continue
                    
                    if not error:
                        break

class RawSingle(BaseFormat):
    def __init__(self, *args, **kwargs):
        if not pillow_ready:
            raise PillowNotInstalled("pillow is not installed")
        
        super().__init__(*args, **kwargs)

    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace
        total = 0

        # In order to add "next chapter" image mark in end of current chapter
        # We need to cache all chapters
        log.info("Preparing to download...")
        cache = []
        # Enable log cache
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for chap_class, images in manga.chapters.iter(**kwargs_iter):
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

        # Construct folder name from first and last chapter
        first_chapter = cache[0][0]
        last_chapter = cache[len(cache) - 1][0]
        path = base_path / sanitize_filename(first_chapter.name + " - " + last_chapter.name)
        path.mkdir(exist_ok=True)

        for index, (chap_class, images) in enumerate(cache):
            start = True

            # Group name will be placed inside the start and end of chapter images
            chap = chap_class.chapter
            chap_name = chap_class.name

            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            # Insert "start of the chapter" image
            img_name = count.get() + '.png'
            img_path = path / img_name
            img = get_mark_image(chap_class)
            img.save(img_path, 'png')

            count.increase()

            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    server_file = img_name

                    img_ext = os.path.splitext(img_name)[1]
                    img_name = count.get() + img_ext

                    img_path = path / img_name

                    log.info('Downloading %s page %s' % (chap_name, page))

                    # Verify file
                    if self.verify and not replace:
                        # Can be True, False, or None
                        verified = verify_sha256(server_file, img_path)
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
                        count.increase()
                        continue
                
                if not error:
                    break
