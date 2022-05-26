import logging
import shutil
import zipfile
import os
from .base import BaseFormat
from .utils import NumberWithLeadingZeros, delete_file, verify_sha256
from ..utils import create_chapter_folder, write_details
from ..downloader import ChapterPageDownloader

path_exists = lambda x: os.path.exists(x)

log = logging.getLogger(__name__)

class Tachiyomi(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace

        # Write details.json for tachiyomi local manga
        details_path = base_path / 'details.json'
        log.info('Writing details.json')
        write_details(manga, details_path)

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

class TachiyomiZip(BaseFormat):
    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace
        worker = self.create_worker()

        # Write details.json for tachiyomi local manga
        details_path = base_path / 'details.json'
        log.info('Writing details.json')
        write_details(manga, details_path)

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

            chapter_zip_path = base_path / (chap_name + '.zip')
            if chapter_zip_path.exists() and replace:
                delete_file(chapter_zip_path)

            if path_exists(chapter_zip_path):
                chapter_zip = zipfile.ZipFile(str(chapter_zip_path), "a")
            else:
                chapter_zip = zipfile.ZipFile(str(chapter_zip_path), "w")

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
                    # Make sure zipfile is opened in append mode
                    if chapter_zip.mode == "a" and self.verify and not replace:
                        # Can be True, False, or None
                        try:
                            content = chapter_zip.read(img_name)
                        except KeyError:
                            # File is not exist
                            verified = None
                        else:
                            verified = verify_sha256(server_file, data=content)
                    elif not self.verify or chapter_zip.mode == "w":
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
                        wrap = lambda: chapter_zip.writestr(img_name, img_path.read_bytes())
                        
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
