import io
import logging
import shutil
import zipfile
import os

from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import get_mark_image
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
        for vol, chap, chap_name, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
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
                error = False
                for page, img_url, img_name in images.iter():
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
        count = 0

        # In order to add "next chapter" image mark in end of current chapter
        # We need to cache all chapters
        log.info("Preparing to download...")
        cache = []
        # Enable log cache
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for vol, chap, chap_name, images in manga.chapters.iter_chapter_images(**kwargs_iter):
            item = [vol, chap, chap_name, images]
            cache.append(item)

        # Construct .cbz filename from first and last chapter
        first_chapter = cache[0][2]
        last_chapter = cache[len(cache) - 1][2]
        manga_zip_path = base_path / sanitize_filename(first_chapter + " - " + last_chapter + '.cbz')
        manga_zip = zipfile.ZipFile(
            str(manga_zip_path),
            "a" if path_exists(manga_zip_path) else "w"
        )

        # Begin downloading
        for index, item in enumerate(cache):
            vol = item[0]
            chap = item[1]
            chap_name = item[2]
            images = item[3]

            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            chapter_path = create_chapter_folder(base_path, chap_name)

            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    img_path = chapter_path / img_name

                    file = '%s_%s' % (count, img_name)

                    log.info('Downloading %s page %s' % (chap_name, page))

                    try:
                        manga_zip.getinfo(file)
                    except KeyError:
                        img_exist = False
                    else:
                        img_exist = True
                    
                    if img_exist and not self.replace:
                        log.info("File exist and replace is False, cancelling download...")
                        count += 1
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
                        wrap = lambda: manga_zip.writestr(file, img_path.read_bytes())
                        
                        # KeyboardInterrupt safe
                        worker.submit(wrap)
                        
                        # And then remove it original file
                        os.remove(img_path)

                        count += 1
                        continue
                
                if not error:
                    break            

            # get mark image
            mark_img_file = '%s_mark_image.png' % count
            mark_img = get_mark_image(chap_name, cache, index)
            fp = io.BytesIO()
            mark_img.save(fp, 'png')

            # Insert mark image
            wrap = lambda: manga_zip.writestr(mark_img_file, fp.getvalue())
            worker.submit(wrap)

            count += 1

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()