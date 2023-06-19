# MIT License

# Copyright (c) 2022-present Rahman Yusuf

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

import logging
import shutil
import zipfile
import os
import xml.etree.ElementTree as ET

from tqdm import tqdm
from .base import (
    ConvertedChaptersFormat,
    ConvertedVolumesFormat,
    ConvertedSingleFormat
)
from .utils import (
    get_chapter_info,
    NumberWithLeadingZeros,
    verify_sha256,
    get_volume_cover
)
from ..utils import create_directory, delete_file
from ..progress_bar import progress_bar_manager as pbm

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

class CBZFile:
    file_ext = ".cbz"

    def convert(self, zip_obj, images):
        pbm.set_convert_total(len(images))
        progress_bar = pbm.get_convert_pb(recreate=not pbm.stacked)

        for im_path in images:
            zip_obj.write(im_path, im_path.name)
            progress_bar.update(1)                

        zip_obj.close()

    def check_dependecies(self):
        pass

    def make_zip(self, path):
        from ..config import env

        return zipfile.ZipFile(
            path,
            "a" if os.path.exists(path) else "w",
            compression=env.zip_compression_type,
            compresslevel=env.zip_compression_level
        )

    def insert_ch_info_img(self, zip_obj, worker, chapter, count, path):
        img_name = count.get() + '.png'
        img_path = path / img_name

        # Make sure we never duplicated it
        write_ch_info_image = False
        try:
            zip_obj.getinfo(img_name)
        except KeyError:
            write_ch_info_image = self.config.use_chapter_cover

        # Insert chapter info (cover) image
        if write_ch_info_image:
            get_chapter_info(self.manga, chapter, img_path)
            worker.submit(lambda: zip_obj.write(img_path, img_name))
            count.increase()

    def insert_vol_cover_img(self, zip_obj, worker, volume, count, path):
        # Insert volume cover
        # Make sure we never duplicate it
        img_name = count.get() + ".png"
        img_path = path / img_name

        write_vol_cover = False
        try:
            zip_obj.getinfo(img_name)
        except KeyError:
            write_vol_cover = self.config.use_volume_cover
        
        if write_vol_cover:
            get_volume_cover(self.manga, volume, img_path, self.replace)
            worker.submit(lambda: zip_obj.write(img_path, img_name))
            count.increase()

class ComicBookArchive(ConvertedChaptersFormat, CBZFile):
    def on_prepare(self, file_path, chapter, images):
        self.chapter_zip = self.make_zip(file_path)

        # Generate 'ComicInfo.xml' data
        xml_data = generate_Comicinfo(self.manga, chapter)

        # Write 'ComicInfo.xml' to .cbz file
        # And make sure that we don't write it twice or more
        if 'ComicInfo.xml' not in self.chapter_zip.namelist():
            wrap = lambda: self.chapter_zip.writestr('ComicInfo.xml', ET.tostring(xml_data))
            # KeyboardInterrupt safe
            self.worker.submit(wrap)

    def on_finish(self, file_path, chapter, images):
        chap_name = chapter.get_simplified_name()

        pbm.logger.info(f"{chap_name} has finished download, converting to cbz...")
        self.worker.submit(lambda: self.convert(self.chapter_zip, images))

class ComicBookArchiveVolume(ConvertedVolumesFormat, CBZFile):
    def on_prepare(self, file_path, volume, count):
        volume_name = self.get_volume_name(volume)
        self.volume_zip = self.make_zip(file_path)
        self.volume_path = create_directory(volume_name, self.path)

        self.insert_vol_cover_img(self.volume_zip, self.worker, volume, count, self.volume_path)

    def on_iter_chapter(self, file_path, chapter, count):
        self.insert_ch_info_img(self.volume_zip, self.worker, chapter, count, self.volume_path)

    def on_finish(self, file_path, volume, images):
        volume_name = self.get_volume_name(volume)
        pbm.logger.info(f"{volume_name} has finished download, converting to cbz...")

        self.worker.submit(lambda: self.convert(self.volume_zip, images))

class ComicBookArchiveSingle(ConvertedSingleFormat, CBZFile):
    def on_prepare(self, file_path, base_path):
        self.images_directory = base_path
        self.zip = self.make_zip(file_path)

    def on_iter_chapter(self, file_path, chapter, count):
        self.insert_ch_info_img(self.zip, self.worker, chapter, count, self.images_directory)

    def on_finish(self, file_path, images):
        pbm.logger.info(f"Manga '{self.manga.title}' has finished download, converting to cbz...")

        self.worker.submit(lambda: self.convert(self.zip, images))
        