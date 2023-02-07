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

import logging
import io
import os
import time
import math
import shutil

from tqdm import tqdm
from .base import (
    ConvertedChaptersFormat,
    ConvertedVolumesFormat,
    ConvertedSingleFormat
)
from .utils import (
    NumberWithLeadingZeros,
    get_chapter_info,
    get_volume_cover
)
from ..errors import PillowNotInstalled
from ..utils import create_directory, delete_file

log = logging.getLogger(__name__)

try:
    from PIL import (
        Image,
        ImageFile,
        ImageSequence,
        PdfParser,
        __version__,
        features
    )
except ImportError:
    pillow_ready = False
else:
    pillow_ready = True

class _PageRef:
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
    
    def __call__(self):
        return self._func(*self._args, **self._kwargs)

class PDFPlugin:
    def __init__(self, ims):
        # "Circular Imports" problem
        from ..config import config

        self.tqdm = tqdm(
            desc='pdf_progress',
            total=len(ims),
            initial=0,
            unit='item',
            disable=config.no_progress_bar
        )

        self.register_pdf_handler()

    def check_truncated(self, img):
        # Pillow won't load truncated images
        # See https://github.com/python-pillow/Pillow/issues/1510
        # Image reference: https://mangadex.org/chapter/1615adcb-5167-4459-8b12-ee7cfbdb10d9/16
        err = None
        try:
            img.load()
        except OSError as e:
            err = e
        else:
            return False
        
        if err and 'broken data stream' in str(err):
            ImageFile.LOAD_TRUNCATED_IMAGES = True
        elif err:
            # Other error
            raise err
        
        # Load it again
        img.load()

        return True

    def _save_all(self, im, fp, filename):
        self._save(im, fp, filename, save_all=True)

    # This was modified version of Pillow/PdfImagePlugin.py version 9.3.0
    # The images will be automatically converted to RGB and closed when done converting to PDF
    def _save(self, im, fp, filename, save_all=False):
        is_appending = im.encoderinfo.get("append", False)
        if is_appending:
            existing_pdf = PdfParser.PdfParser(f=fp, filename=filename, mode="r+b")
        else:
            existing_pdf = PdfParser.PdfParser(f=fp, filename=filename, mode="w+b")

        resolution = im.encoderinfo.get("resolution", 72.0)

        info = {
            "title": None
            if is_appending
            else os.path.splitext(os.path.basename(filename))[0],
            "author": None,
            "subject": None,
            "keywords": None,
            "creator": None,
            "producer": None,
            "creationDate": None if is_appending else time.gmtime(),
            "modDate": None if is_appending else time.gmtime(),
        }
        for k, default in info.items():
            v = im.encoderinfo.get(k) if k in im.encoderinfo else default
            if v:
                existing_pdf.info[k[0].upper() + k[1:]] = v

        #
        # make sure image data is available
        im.load()

        existing_pdf.start_writing()
        existing_pdf.write_header()
        existing_pdf.write_comment(f"created by Pillow {__version__} PDF driver")

        #
        # pages
        encoderinfo = im.encoderinfo.copy()
        ims = [im]
        if save_all:
            append_images = im.encoderinfo.get("append_images", [])
            ims.extend(append_images)

        number_of_pages = 0
        image_refs = []
        page_refs = []
        contents_refs = []
        for im_ref in ims:
            img = im_ref() if isinstance(im_ref, _PageRef) else im_ref
            im_number_of_pages = 1
            if save_all:
                try:
                    im_number_of_pages = img.n_frames
                except AttributeError:
                    # Image format does not have n_frames.
                    # It is a single frame image
                    pass
            number_of_pages += im_number_of_pages
            for i in range(im_number_of_pages):
                image_refs.append(existing_pdf.next_object_id(0))
                page_refs.append(existing_pdf.next_object_id(0))
                contents_refs.append(existing_pdf.next_object_id(0))
                existing_pdf.pages.append(page_refs[-1])
            
            # Reduce Opened files
            if isinstance(im_ref, _PageRef):
                img.close()

        #
        # catalog and list of pages
        existing_pdf.write_catalog()

        if ImageFile.LOAD_TRUNCATED_IMAGES:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

        page_number = 0
        for im_ref in ims:
            im = im_ref() if isinstance(im_ref, _PageRef) else im_ref

            truncated = self.check_truncated(im)

            if im.mode != 'RGB':
                # Convert to RGB mode
                im_sequence = im.convert('RGB')

                # Close image to save memory
                im.close()
            else:
                # Already in RGB mode
                im_sequence = im

            # Copy necessary encoderinfo to new image
            im_sequence.encoderinfo = encoderinfo.copy()

            im_pages = ImageSequence.Iterator(im_sequence) if save_all else [im_sequence]
            for im in im_pages:
                # FIXME: Should replace ASCIIHexDecode with RunLengthDecode
                # (packbits) or LZWDecode (tiff/lzw compression).  Note that
                # PDF 1.2 also supports Flatedecode (zip compression).

                bits = 8
                params = None
                decode = None

                #
                # Get image characteristics

                width, height = im.size

                if im.mode == "1":
                    if features.check("libtiff"):
                        filter = "CCITTFaxDecode"
                        bits = 1
                        params = PdfParser.PdfArray(
                            [
                                PdfParser.PdfDict(
                                    {
                                        "K": -1,
                                        "BlackIs1": True,
                                        "Columns": width,
                                        "Rows": height,
                                    }
                                )
                            ]
                        )
                    else:
                        filter = "DCTDecode"
                    colorspace = PdfParser.PdfName("DeviceGray")
                    procset = "ImageB"  # grayscale
                elif im.mode == "L":
                    filter = "DCTDecode"
                    # params = f"<< /Predictor 15 /Columns {width-2} >>"
                    colorspace = PdfParser.PdfName("DeviceGray")
                    procset = "ImageB"  # grayscale
                elif im.mode == "P":
                    filter = "ASCIIHexDecode"
                    palette = im.getpalette()
                    colorspace = [
                        PdfParser.PdfName("Indexed"),
                        PdfParser.PdfName("DeviceRGB"),
                        255,
                        PdfParser.PdfBinary(palette),
                    ]
                    procset = "ImageI"  # indexed color
                elif im.mode == "RGB":
                    filter = "DCTDecode"
                    colorspace = PdfParser.PdfName("DeviceRGB")
                    procset = "ImageC"  # color images
                elif im.mode == "CMYK":
                    filter = "DCTDecode"
                    colorspace = PdfParser.PdfName("DeviceCMYK")
                    procset = "ImageC"  # color images
                    decode = [1, 0, 1, 0, 1, 0, 1, 0]
                else:
                    raise ValueError(f"cannot save mode {im.mode}")

                #
                # image

                op = io.BytesIO()

                if filter == "ASCIIHexDecode":
                    ImageFile._save(im, op, [("hex", (0, 0) + im.size, 0, im.mode)])
                elif filter == "CCITTFaxDecode":
                    im.save(
                        op,
                        "TIFF",
                        compression="group4",
                        # use a single strip
                        strip_size=math.ceil(im.width / 8) * im.height,
                    )
                elif filter == "DCTDecode":
                    Image.SAVE["JPEG"](im, op, filename)
                elif filter == "FlateDecode":
                    ImageFile._save(im, op, [("zip", (0, 0) + im.size, 0, im.mode)])
                elif filter == "RunLengthDecode":
                    ImageFile._save(im, op, [("packbits", (0, 0) + im.size, 0, im.mode)])
                else:
                    raise ValueError(f"unsupported PDF filter ({filter})")

                stream = op.getvalue()
                if filter == "CCITTFaxDecode":
                    stream = stream[8:]
                    filter = PdfParser.PdfArray([PdfParser.PdfName(filter)])
                else:
                    filter = PdfParser.PdfName(filter)

                existing_pdf.write_obj(
                    image_refs[page_number],
                    stream=stream,
                    Type=PdfParser.PdfName("XObject"),
                    Subtype=PdfParser.PdfName("Image"),
                    Width=width,  # * 72.0 / resolution,
                    Height=height,  # * 72.0 / resolution,
                    Filter=filter,
                    BitsPerComponent=bits,
                    Decode=decode,
                    DecodeParms=params,
                    ColorSpace=colorspace,
                )

                #
                # page

                existing_pdf.write_page(
                    page_refs[page_number],
                    Resources=PdfParser.PdfDict(
                        ProcSet=[PdfParser.PdfName("PDF"), PdfParser.PdfName(procset)],
                        XObject=PdfParser.PdfDict(image=image_refs[page_number]),
                    ),
                    MediaBox=[
                        0,
                        0,
                        width * 72.0 / resolution,
                        height * 72.0 / resolution,
                    ],
                    Contents=contents_refs[page_number],
                )

                #
                # page contents

                page_contents = b"q %f 0 0 %f 0 0 cm /image Do Q\n" % (
                    width * 72.0 / resolution,
                    height * 72.0 / resolution,
                )

                existing_pdf.write_obj(contents_refs[page_number], stream=page_contents)

                self.tqdm.update(1)
                page_number += 1
            
            # Close image to save memory
            im_sequence.close()

            # For security sake
            if truncated:
                ImageFile.LOAD_TRUNCATED_IMAGES = False

        #
        # trailer
        existing_pdf.write_xref_and_trailer()
        if hasattr(fp, "flush"):
            fp.flush()
        existing_pdf.close()

    def close_progress_bar(self):
        self.tqdm.close()

    def register_pdf_handler(self):
        Image.init()

        Image.register_save('PDF', self._save)
        Image.register_save_all('PDF', self._save_all)
        Image.register_extension('PDF', '.pdf')

        Image.register_mime("PDF", "application/pdf")

class PDFFile:
    file_ext = ".pdf"

    def check_dependecies(self):
        if not pillow_ready:
            raise PillowNotInstalled("pillow is not installed")

    def convert(self, imgs, target):
        pdf_plugin = PDFPlugin(imgs)

        # Because images from BaseFormat.get_images() was just bunch of pathlib.Path
        # objects, we need convert it to _PageRef for be able Modified Pillow can convert it
        images = []
        for im in imgs:
            images.append(_PageRef(Image.open, im))
        
        im_ref = images.pop(0)
        im = im_ref()

        pdf_plugin.check_truncated(im)

        im.save(
            target,
            save_all=True,
            append_images=images
        )

        pdf_plugin.close_progress_bar()

    def insert_ch_info_img(self, images, chapter, path, count):
        """Insert chapter info (cover) image"""
        img_name = count.get() + '.png'
        img_path = path / img_name

        if self.config.use_chapter_cover:
            get_chapter_info(self.manga, chapter, img_path)
            images.append(img_path)
            count.increase()

    def insert_vol_cover_img(self, images, volume, path, count):
        """Insert volume cover"""
        img_name = count.get() + '.png'
        img_path = path / img_name

        if self.config.use_volume_cover:
            get_volume_cover(self.manga, volume, img_path, self.replace)
            images.append(img_path)
            count.increase()

class PDF(ConvertedChaptersFormat, PDFFile):
    def download_chapters(self, worker, chapters):
        # Begin downloading
        for chap_class, chap_images in chapters:
            chap_name = chap_class.get_simplified_name()
            count = NumberWithLeadingZeros(0)

            pdf_file = self.path / (chap_name + self.file_ext)
            if pdf_file.exists():

                if self.replace:
                    delete_file(pdf_file)
                elif self.check_fi_completed(chap_name):
                    log.info(f"'{pdf_file.name}' is exist and replace is False, cancelling download...")

                    self.add_fi(
                        name=chap_name,
                        id=chap_class.id,
                        path=pdf_file,
                    )
                    continue

            chapter_path = create_directory(chap_name, self.path)

            images = self.get_images(chap_class, chap_images, chapter_path, count)
            log.info(f"{chap_name} has finished download, converting to pdf...")

            # Save it as pdf
            worker.submit(lambda: self.convert(images, pdf_file))

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

            self.add_fi(
                name=chap_name,
                id=chap_class.id,
                path=pdf_file,
            )

class PDFVolume(ConvertedVolumesFormat, PDFFile):
    def download_volumes(self, worker, volumes):
        # Begin downloading
        for volume, chapters in volumes.items():
            images = []
            count = NumberWithLeadingZeros(0)

            # Build volume folder name
            vol_name = self.get_volume_name(volume)

            pdf_name = vol_name + self.file_ext
            pdf_file = self.path / pdf_name

            if pdf_file.exists():
                if self.replace:
                    delete_file(pdf_file)
                elif self.check_fi_completed(vol_name):
                    log.info(f"'{pdf_file.name}' is exist and replace is False, cancelling download...")
                    self.add_fi(vol_name, None, pdf_file, chapters)
                    return

            # Create volume folder
            volume_path = create_directory(vol_name, self.path)

            self.insert_vol_cover_img(images, volume, volume_path, count)

            for chap_class, chap_images in chapters:
                self.insert_ch_info_img(images, chap_class, volume_path, count)

                images.extend(self.get_images(chap_class, chap_images, volume_path, count))

            log.info(f"{vol_name} has finished download, converting to pdf...")

            # Save it as pdf
            worker.submit(lambda: self.convert(images, pdf_file))

            # Remove original chapter folder
            shutil.rmtree(volume_path, ignore_errors=True)

            self.add_fi(vol_name, None, pdf_file, chapters)

class PDFSingle(ConvertedSingleFormat, PDFFile):
    def download_single(self, worker, total, merged_name, chapters):
        manga = self.manga
        images = []
        count = NumberWithLeadingZeros(0)
        pdf_file = self.path / (merged_name + self.file_ext)

        if pdf_file.exists():
            if self.replace:
                delete_file(pdf_file)
            elif self.check_fi_completed(merged_name):
                log.info(f"'{pdf_file.name}' is exist and replace is False, cancelling download...")
                self.add_fi(merged_name, None, pdf_file, chapters)
                return

        path = create_directory(merged_name, self.path)

        for chap_class, chap_images in chapters:
            self.insert_ch_info_img(images, chap_class, path, count)

            images.extend(self.get_images(chap_class, chap_images, path, count))

        log.info("Manga \"%s\" has finished download, converting to pdf..." % manga.title)

        # Save it as pdf
        worker.submit(lambda: self.convert(images, pdf_file))

        # Remove downloaded images
        shutil.rmtree(path, ignore_errors=True)

        self.add_fi(merged_name, None, pdf_file, chapters)
