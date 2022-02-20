import logging
import os
import shutil
from .base import BaseFormat
from ..errors import PillowNotInstalled
from ..utils import create_chapter_folder
from ..downloader import ChapterPageDownloader

log = logging.getLogger(__name__)

# For keyboardInterrupt handler
_cleanup_jobs = []

try:
    from PIL import Image
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
