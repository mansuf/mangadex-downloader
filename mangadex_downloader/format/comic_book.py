# MIT License

# Copyright (c) 2022 Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
import logging
import shutil
import zipfile
import os
import xml.etree.ElementTree as ET

from tqdm import tqdm
from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import get_chapter_info, NumberWithLeadingZeros
from ..utils import create_directory, delete_file
from ..errors import PillowNotInstalled

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
    def convert(self, zip_obj, images):
        progress_bar = tqdm(
            desc='cbz_progress',
            total=len(images),
            initial=0,
            unit='item',
            disable=self.config.no_progress_bar
        )

        for im_path in images:
            zip_obj.write(im_path, im_path.name)
            progress_bar.update(1)                

        progress_bar.close()

    def make_zip(self, path):
        from ..config import env

        return zipfile.ZipFile(
            path,
            "a" if os.path.exists(path) else "w",
            compression=env.zip_compression_type,
            compresslevel=env.zip_compression_level
        )

    def main(self):
        manga = self.manga
        worker = self.create_worker()

        # Begin downloading
        for chap_class, images in manga.chapters.iter(**self.kwargs_iter):
            chap_name = chap_class.get_simplified_name()

            # Check if .cbz file is exist or not
            chapter_zip_path = self.path / (chap_name + '.cbz')
            if chapter_zip_path.exists():

                if self.replace:
                    delete_file(chapter_zip_path)
                else:
                    log.info(f"'{chapter_zip_path.name}' is exist and replace is False, cancelling download...")
                    continue

            chapter_path = create_directory(chap_name, self.path)

            chapter_zip = self.make_zip(chapter_zip_path)

            # Generate 'ComicInfo.xml' data
            xml_data = generate_Comicinfo(manga, chap_class)

            # Write 'ComicInfo.xml' to .cbz file
            # And make sure that we don't write it twice or more
            if 'ComicInfo.xml' not in chapter_zip.namelist():
                wrap = lambda: chapter_zip.writestr('ComicInfo.xml', ET.tostring(xml_data))
                # KeyboardInterrupt safe
                worker.submit(wrap)

            count = NumberWithLeadingZeros(chap_class.pages)
            images = self.get_images(chap_class, images, chapter_path, count)

            log.info(f"{chap_name} has finished download, converting to cbz...")

            # KeyboardInterrupt safe
            worker.submit(lambda: self.convert(chapter_zip, images))

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class ComicBookArchiveVolume(ComicBookArchive):
    def main(self):
        manga = self.manga
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
        for chap_class, chap_images in manga.chapters.iter(**kwargs_iter):
            append_cache(chap_class.volume, [chap_class, chap_images])

        # Begin downloading
        for volume, chapters in cache.items():
            num = 0
            images = []

            for chap_class, _ in chapters:
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

            volume_zip_path = self.path / (volume + '.cbz')

            # Check if exist or not
            if volume_zip_path.exists():
                
                if self.replace:
                    delete_file(volume_zip_path)
                else:
                    log.info(f"{volume_zip_path.name} is exist and replace is False, cancelling download...")
                    continue

            # Create volume folder
            volume_path = create_directory(volume, self.path)

            volume_zip = self.make_zip(volume_zip_path)

            for chap_class, chap_images in chapters:
                img_name = count.get() + '.png'
                img_path = volume_path / img_name

                # Make sure we never duplicated it
                write_start_image = False
                try:
                    volume_zip.getinfo(img_name)
                except KeyError:
                    write_start_image = True

                if self.no_chapter_info:
                    write_start_image = False

                # Insert "start of the chapter" image
                if write_start_image:
                    get_chapter_info(chap_class, img_path, self.replace)
                    worker.submit(lambda: volume_zip.write(img_path, img_name))

                count.increase()

                images.extend(self.get_images(chap_class, chap_images, volume_path, count))

            log.info(f"{volume} has finished download, converting to cbz...")

            worker.submit(lambda: self.convert(volume_zip, images))
                
            # Remove original chapter folder
            shutil.rmtree(volume_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class ComicBookArchiveSingle(ComicBookArchive):
    def main(self):
        images = []
        manga = self.manga
        worker = self.create_worker()
        result_cache = self.get_fmt_single_cache(manga)

        if result_cache is None:
            # The chapters is empty
            # there is nothing we can download
            worker.shutdown()
            return
        
        cache, total, merged_name = result_cache

        count = NumberWithLeadingZeros(total)
        manga_zip_path = self.path / (merged_name + '.cbz')

        # Check if exist or not
        if manga_zip_path.exists():
            if self.replace:
                delete_file(manga_zip_path)
            else:
                log.info(f"{manga_zip_path.name} is exist and replace is False, cancelling download...")
                return

        manga_zip = self.make_zip(manga_zip_path)
        path = create_directory(merged_name, self.path)

        for chap_class, chap_images in cache:
            img_name = count.get() + '.png'
            img_path = path / img_name

            # Make sure we never duplicated it
            write_start_image = False
            try:
                manga_zip.getinfo(img_name)
            except KeyError:
                write_start_image = True

            if self.no_chapter_info:
                write_start_image = False

            # Insert "start of the chapter" image
            if write_start_image:
                get_chapter_info(chap_class, img_path, self.replace)
                worker.submit(lambda: manga_zip.write(img_path, img_name))

            count.increase()

            # Begin downloading
            images.extend(self.get_images(chap_class, chap_images, path, count))

        # Convert
        log.info(f"Manga '{manga.title}' has finished download, converting to cbz...")
        worker.submit(lambda: self.convert(manga_zip, images))

        # Remove downloaded images
        shutil.rmtree(path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()
