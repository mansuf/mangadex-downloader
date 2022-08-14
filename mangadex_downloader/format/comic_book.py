import io
import logging
import shutil
import zipfile
import os
import xml.etree.ElementTree as ET

from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import get_mark_image, NumberWithLeadingZeros, delete_file, verify_sha256
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


def generate_Comicinfo(manga, chapter):
    xml_root = ET.Element('ComicInfo',
                          {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                           'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema'})
    xml_series = ET.SubElement(xml_root, 'Series')
    xml_series.text = manga._title

    if len(manga.authors) > 0:
        author_str = ""
        for author in manga.authors:
            author_str = author_str + ',' + author
        xml_author = ET.SubElement(xml_root, 'Writer')
        xml_author.text = author_str[1:]

    if len(manga.artists) > 0:
        artist_str = ""
        for artist in manga.artists:
            artist_str = artist_str + ',' + artist
        xml_artist = ET.SubElement(xml_root, 'Penciller')
        xml_artist.text = artist_str[1:]

    if len(manga.genres) > 0:
        genre_str = ""
        for genre in manga.genres:
            genre_str = genre_str + ',' + genre
        xml_genre = ET.SubElement(xml_root, 'Genre')
        xml_genre.text = genre_str[1:]

    xml_summary = ET.SubElement(xml_root, 'Summary')
    xml_summary.text = manga.description

    if len(manga.alternative_titles) > 0:
        alt_str = ""
        for alt in manga.alternative_titles:
            alt_str = alt_str + ',' + alt
        xml_alt = ET.SubElement(xml_root, 'AlternateSeries')
        xml_alt.text = alt_str[1:]

    if chapter is not None:
        if chapter.volume is not None:
            xml_vol = ET.SubElement(xml_root, 'Volume')
            xml_vol.text = str(chapter.volume)

        if chapter.chapter is not None:
            xml_num = ET.SubElement(xml_root, 'Number')
            xml_num.text = str(chapter.chapter)

        xml_title = ET.SubElement(xml_root, 'Title')
        xml_title.text = chapter.name

        xml_lang = ET.SubElement(xml_root, 'LanguageISO')
        xml_lang.text = str(chapter.language.value)

    xml_pc = ET.SubElement(xml_root, 'PageCount')
    xml_pc.text = str(chapter.pages)

    xml_si = ET.SubElement(xml_root, 'ScanInformation')
    xml_si.text = chapter.groups_name

    return xml_root


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
            chap_name = chap_class.get_simplified_name()
            chap_extended_name = chap_class.get_name()
            xml_data = generate_Comicinfo(manga, chap_class)

            # Fetching chapter images
            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            chapter_path = create_chapter_folder(base_path, chap_name)

            chapter_zip_path = base_path / (chap_name + '.cbz')
            if chapter_zip_path.exists() and replace:
                delete_file(chapter_zip_path)

            chapter_zip = zipfile.ZipFile(
                str(chapter_zip_path),
                "a" if path_exists(chapter_zip_path) else "w"
            )

            if 'ComicInfo.xml' not in chapter_zip.namelist():
                wrap = lambda: chapter_zip.writestr('ComicInfo.xml', ET.tostring(xml_data))
                # KeyboardInterrupt safe
                worker.submit(wrap)

            while True:
                # Fix #10
                # Some old programs wouldn't display images correctly
                count = NumberWithLeadingZeros(images.iter())

                error = False
                for page, img_url, img_name in images.iter(log_info=True):
                    server_file = img_name

                    img_ext = os.path.splitext(img_name)[1]
                    img_name = count.get() + img_ext

                    img_path = chapter_path / img_name

                    log.info('Downloading %s page %s' % (chap_extended_name, page))

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
                volume = f'Vol. {chap_class.volume}'
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
                img_name = count.get() + '.png'

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
                    for page, img_url, img_name in images.iter(log_info=True):
                        server_file = img_name

                        img_ext = os.path.splitext(img_name)[1]
                        img_name = count.get() + img_ext

                        img_path = volume_path / img_name

                        log.info('Downloading %s page %s' % (chap_name, page))

                        # Verify file
                        # Make sure zipfile is opened in append mode
                        if volume_zip.mode == "a" and self.verify and not replace:
                            # Can be True, False, or None
                            try:
                                content = volume_zip.read(img_name)
                            except KeyError:
                                # File is not exist
                                verified = None
                            else:
                                verified = verify_sha256(server_file, data=content)
                        elif not self.verify or volume_zip.mode == "w":
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
        manga_zip_path = base_path / sanitize_filename(
            first_chapter.simple_name + " - " + last_chapter.simple_name + '.cbz'
        )
        manga_zip = zipfile.ZipFile(
            str(manga_zip_path),
            "a" if path_exists(manga_zip_path) else "w"
        )

        for chap_class, images in cache:
            # Insert "start of the chapter" image
            img_name = count.get() + '.png'

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
                for page, img_url, img_name in images.iter(log_info=True):
                    server_file = img_name

                    img_ext = os.path.splitext(img_name)[1]
                    img_name = count.get() + img_ext

                    img_path = chapter_path / img_name

                    log.info('Downloading %s page %s' % (chap_name, page))

                    # Verify file
                    # Make sure zipfile is opened in append mode
                    if manga_zip.mode == "a" and self.verify and not replace:
                        # Can be True, False, or None
                        try:
                            content = manga_zip.read(img_name)
                        except KeyError:
                            # File is not exist
                            verified = None
                        else:
                            verified = verify_sha256(server_file, data=content)
                    elif not self.verify or manga_zip.mode == "w":
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
