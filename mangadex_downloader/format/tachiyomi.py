import logging
from .base import BaseFormat
from ..utils import create_chapter_folder, write_details
from ..downloader import ChapterPageDownloader

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
        for vol, chap, chap_name, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
            # Fetching chapter images
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

                    log.info('Downloading %s page %s' % (chap_name, page))
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
                        continue
                
                if not error:
                    break
            