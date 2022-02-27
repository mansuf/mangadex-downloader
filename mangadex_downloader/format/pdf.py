import logging
import os
import shutil

from pathvalidate import sanitize_filename
from .base import BaseFormat
from ..errors import PillowNotInstalled
from ..utils import create_chapter_folder
from ..downloader import ChapterPageDownloader

log = logging.getLogger(__name__)

# For keyboardInterrupt handler
_cleanup_jobs = []

# Some constants for PDFWrap
rgb_white = (255, 255, 255)
rgb_black = (0, 0, 0)
font_family = "arial.ttf"
font_size = 30
image_size = (720, int(1100 / 1.25))
image_mode = "RGB"
text_pos = (150, int(500 / 1.25))
text_align = "center"

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pillow_ready = False
else:
    pillow_ready = True

# Helper function to delete file
def delete_file(file):
    # If 10 attempts is failed to delete file (ex: PermissionError, or etc.)
    # raise error
    err = None
    for _ in range(10):
        try:
            os.remove(file)
        except Exception as e:
            err = e
        else:
            break
    if err is not None:
        log.debug("Failed to delete file \"%s\"" % file)
        raise err

class PDF(BaseFormat):
    def __init__(self, *args, **kwargs):
        if not pillow_ready:
            raise PillowNotInstalled("pillow is not installed")

        super().__init__(*args, **kwargs)
        self.register_keyboardinterrupt_handler()

    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace

        # Begin downloading
        for vol, chap, chap_name, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
            # Fetching chapter images
            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            # This file is for keep track finished images chapter converted to pdf
            # If gets deleted, the chapter will marked as finished download
            # How it work:
            # It will check one of chapter image is exist in .unfinished file
            # if exist, it will ignore it (if replace is False). Otherwise it will download it and put the image name
            # to .unfinished file.
            unfinished_chapter_path = base_path / (chap_name + '.unfinished')

            if replace:
                open(unfinished_chapter_path, 'w').close()

            exists = unfinished_chapter_path.exists()
            if exists:
                unfinished_chapter = unfinished_chapter_path.read_text().splitlines()
            else:
                unfinished_chapter = []

            pdf_file = base_path / (chap_name + '.pdf')
            def pdf_file_exists(converting=False):
                if replace and not converting:
                    try:
                        delete_file(pdf_file)
                    except FileNotFoundError:
                        pass
                return os.path.exists(pdf_file)

            if pdf_file_exists() and not exists and not replace:
                log.info("Chapter PDF file exist and replace is False, cancelling download...")
                continue

            chapter_path = create_chapter_folder(base_path, chap_name)

            tracker = open(unfinished_chapter_path, "a" if exists else "w")

            # In case KeyboardInterrupt is called
            _cleanup_jobs.append(lambda: tracker.close())

            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    img_path = chapter_path / img_name

                    log.info('Downloading %s page %s' % (chap_name, page))

                    if img_name in unfinished_chapter and not self.replace:
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
                        def convert_pdf():
                            # Begin converting to PDF
                            img = Image.open(img_path)
                            converted_img = img.convert('RGB')

                            def cleanup():
                                img.close()
                                converted_img.close()

                            _cleanup_jobs.append(cleanup)

                            # Save it to PDF
                            converted_img.save(pdf_file, save_all=True, append=True if pdf_file_exists(True) else False)                        

                            # Close the image
                            img.close()
                            converted_img.close()

                            # And then remove it original file
                            delete_file(img_path)

                            tracker.write(img_name + '\n')
                            tracker.flush()

                        self._submit(convert_pdf)
                        continue
                
                if not error:
                    # Remove .unfinished file
                    tracker.close()
                    delete_file(unfinished_chapter_path)
                    break

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)
        
        # Shutdown queue-based thread process
        self._shutdown()

class PDFWrap(PDF):
    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace

        # In order to add "next chapter" image mark in end of current chapter
        # We need to cache all chapters
        cache = []
        log.debug("Caching chapters...")
        for vol, chap, chap_name, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
            item = [vol, chap, chap_name, images]
            cache.append(item)
        
        # Construct pdf filename from first and last chapter
        first_chapter = cache[0][2]
        last_chapter = cache[len(cache) - 1][2]
        pdf_name = sanitize_filename(first_chapter + " - " + last_chapter + '.pdf')
        pdf_file = base_path / pdf_name

        # This file is for keep track finished images chapter converted to pdf
        # If gets deleted, the manga will marked as finished download
        # How it work:
        # It will check one of chapter image is exist in .finished file
        # if exist, it will ignore it (if replace is False). Otherwise it will download it and put the image name
        # to .finished file.
        finished_chapter_path = base_path / (pdf_name + '.finished')

        if replace:
            open(finished_chapter_path, 'w').close()

        exists = finished_chapter_path.exists()
        if exists:
            finished_chapter = finished_chapter_path.read_text().splitlines()
        else:
            finished_chapter = []

        def pdf_file_exists(converting=False):
            if replace and not converting:
                try:
                    delete_file(pdf_file)
                except FileNotFoundError:
                    pass
            return os.path.exists(pdf_file)

        if pdf_file_exists() and not exists and not replace:
            log.info("Chapter PDF file exist and replace is False, cancelling download...")
            return

        tracker = open(finished_chapter_path, "a" if exists else "w")

        # In case KeyboardInterrupt is called
        _cleanup_jobs.append(lambda: tracker.close())

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

            downloaded = False
            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    img_path = chapter_path / img_name

                    img_name_manifest = "%s_%s" % (chap_name, img_name)

                    log.info('Downloading %s page %s' % (chap_name, page))

                    if img_name_manifest in finished_chapter and not self.replace:
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
                        def convert_pdf():
                            # Begin converting to PDF
                            img = Image.open(img_path)
                            converted_img = img.convert('RGB')

                            def cleanup():
                                img.close()
                                converted_img.close()

                            _cleanup_jobs.append(cleanup)

                            # Save it to PDF
                            converted_img.save(pdf_file, save_all=True, append=True if pdf_file_exists(True) else False)                        

                            # Close the image
                            img.close()
                            converted_img.close()

                            # And then remove it original file
                            delete_file(img_path)

                            tracker.write(img_name_manifest + '\n')
                            tracker.flush()

                        self._submit(convert_pdf)
                        downloaded = True
                
                if not error:
                    break

            # Create image that marked chapter is finished
            def insert_mark_image():
                text = ""
                text += "Finished: " + chap_name
                try:
                    next_chap_name = cache[index + 1]
                except IndexError:
                    pass
                else:
                    text += "\n" + "Next: " + next_chap_name[2]

                font = ImageFont.truetype(font_family, font_size)
                img = Image.new(image_mode, image_size, rgb_white)
                draw = ImageDraw.Draw(img, image_mode)
                draw.text(text_pos, text, rgb_black, font, align='center')

                img.save(pdf_file, save_all=True, append=True if pdf_file_exists(True) else False)   

                img.close()
            
            if downloaded:
                self._submit(insert_mark_image)

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Remove .finished file
        tracker.close()
        delete_file(finished_chapter_path)

        # Shutdown queue-based thread process
        self._shutdown()

        