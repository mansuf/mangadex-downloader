import logging
import io
import os
import time
import shutil

from pathvalidate import sanitize_filename
from tqdm import tqdm
from .base import BaseFormat
from .utils import get_mark_image
from ..errors import PillowNotInstalled
from ..utils import create_chapter_folder
from ..downloader import ChapterPageDownloader

log = logging.getLogger(__name__)

# For keyboardInterrupt handler
_cleanup_jobs = []

try:
    from PIL import (
        Image,
        ImageFile,
        ImageSequence,
        PdfParser,
        __version__
    )
except ImportError:
    pillow_ready = False
else:
    pillow_ready = True

# Helper function to delete file
def delete_file(file):
    # If 10 attempts is failed to delete file (ex: PermissionError, or etc.)
    # raise error
    err = None
    for _ in range(100):
        try:
            os.remove(file)
        except Exception as e:
            err = e
        else:
            break
    if err is not None:
        log.debug("Failed to delete file \"%s\"" % file)
        raise err

class _ChapterMarkImage:
    def __init__(self, func, args) -> None:
        self.func = func
        self.args = args

class PDFPlugin:
    def __init__(self, ims):
        self.tqdm = tqdm(
            desc='pdf_progress',
            total=len(ims),
            initial=0,
            unit='item',
        )

        self.register_pdf_handler()

    def _save_all(self, im, fp, filename):
        self._save(im, fp, filename, save_all=True)

    # This was modified version of Pillow/PdfImagePlugin.py version 9.0.1
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
        ims = [im]
        if save_all:
            append_images = im.encoderinfo.get("append_images", [])
            for append_im in append_images:
                append_im.encoderinfo = im.encoderinfo.copy()
                ims.append(append_im)

        numberOfPages = 0
        image_refs = []
        page_refs = []
        contents_refs = []
        for im in ims:
            im_numberOfPages = 1
            if save_all and not isinstance(im, _ChapterMarkImage):
                try:
                    im_numberOfPages = im.n_frames
                except AttributeError:
                    # Image format does not have n_frames.
                    # It is a single frame image
                    pass
            numberOfPages += im_numberOfPages
            for i in range(im_numberOfPages):
                image_refs.append(existing_pdf.next_object_id(0))
                page_refs.append(existing_pdf.next_object_id(0))
                contents_refs.append(existing_pdf.next_object_id(0))
                existing_pdf.pages.append(page_refs[-1])

        #
        # catalog and list of pages
        existing_pdf.write_catalog()

        pageNumber = 0
        for orig_img in ims:
            # This is mark chapter image
            # Retrieve it first and then convert
            if isinstance(orig_img, _ChapterMarkImage):
                mark_img = orig_img.func(*orig_img.args)
                imSequence = mark_img.convert("RGB")
                imSequence.encoderinfo = orig_img.encoderinfo.copy()
            else:
                # Convert image to RGB
                imSequence = orig_img.convert('RGB')
                imSequence.encoderinfo = orig_img.encoderinfo.copy()

            im_pages = ImageSequence.Iterator(imSequence) if save_all else [imSequence]
            for im in im_pages:
                # FIXME: Should replace ASCIIHexDecode with RunLengthDecode
                # (packbits) or LZWDecode (tiff/lzw compression).  Note that
                # PDF 1.2 also supports Flatedecode (zip compression).

                bits = 8
                params = None
                decode = None

                if im.mode == "1":
                    filter = "DCTDecode"
                    colorspace = PdfParser.PdfName("DeviceGray")
                    procset = "ImageB"  # grayscale
                    bits = 1
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
                elif filter == "DCTDecode":
                    Image.SAVE["JPEG"](im, op, filename)
                elif filter == "FlateDecode":
                    ImageFile._save(im, op, [("zip", (0, 0) + im.size, 0, im.mode)])
                elif filter == "RunLengthDecode":
                    ImageFile._save(im, op, [("packbits", (0, 0) + im.size, 0, im.mode)])
                else:
                    raise ValueError(f"unsupported PDF filter ({filter})")

                #
                # Get image characteristics

                width, height = im.size

                existing_pdf.write_obj(
                    image_refs[pageNumber],
                    stream=op.getvalue(),
                    Type=PdfParser.PdfName("XObject"),
                    Subtype=PdfParser.PdfName("Image"),
                    Width=width,  # * 72.0 / resolution,
                    Height=height,  # * 72.0 / resolution,
                    Filter=PdfParser.PdfName(filter),
                    BitsPerComponent=bits,
                    Decode=decode,
                    DecodeParams=params,
                    ColorSpace=colorspace,
                )

                #
                # page

                existing_pdf.write_page(
                    page_refs[pageNumber],
                    Resources=PdfParser.PdfDict(
                        ProcSet=[PdfParser.PdfName("PDF"), PdfParser.PdfName(procset)],
                        XObject=PdfParser.PdfDict(image=image_refs[pageNumber]),
                    ),
                    MediaBox=[
                        0,
                        0,
                        width * 72.0 / resolution,
                        height * 72.0 / resolution,
                    ],
                    Contents=contents_refs[pageNumber],
                )

                #
                # page contents

                page_contents = b"q %f 0 0 %f 0 0 cm /image Do Q\n" % (
                    width * 72.0 / resolution,
                    height * 72.0 / resolution,
                )

                existing_pdf.write_obj(contents_refs[pageNumber], stream=page_contents)

                self.tqdm.update(1)
                pageNumber += 1
            
            # Close image to save memory
            if not isinstance(orig_img, _ChapterMarkImage):
                orig_img.close()
            imSequence.close()

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

class PDF(BaseFormat):
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

        # Begin downloading
        for vol, chap_class, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
            chap = chap_class.chapter
            chap_name = chap_class.get_name()

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

                        worker.submit(convert_pdf)
                        continue
                
                if not error:
                    # Remove .unfinished file
                    tracker.close()
                    delete_file(unfinished_chapter_path)
                    break

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)
        
        # Shutdown queue-based thread process
        worker.shutdown()

class PDFSingle(PDF):
    def main(self):
        base_path = self.path
        manga = self.manga
        compressed_image = self.compress_img
        replace = self.replace
        worker = self.create_worker()
        imgs = []
        chapter_folders = []

        # In order to add "next chapter" image mark in end of current chapter
        # We need to cache all chapters
        log.info("Preparing to download...")
        cache = []
        # Enable log cache
        kwargs_iter = self.kwargs_iter.copy()
        kwargs_iter['log_cache'] = True
        for vol, chap_class, images in manga.chapters.iter_chapter_images(**self.kwargs_iter):
            item = [vol, chap_class, images]
            cache.append(item)
        
        # Construct pdf filename from first and last chapter
        first_chapter = cache[0][1]
        last_chapter = cache[len(cache) - 1][1]
        pdf_name = sanitize_filename(first_chapter.name + " - " + last_chapter.name + '.pdf')
        pdf_file = base_path / pdf_name

        # This file is for tracking downloaded chapter images
        # if gets deleted, the chapter images will be re-downloaded from zero
        finished_download_path = base_path / (pdf_name + '.finished_download')

        if replace:
            open(finished_download_path, "w").close()
        
        exists_download = finished_download_path.exists()
        if exists_download:
            finished_download = finished_download_path.read_text().splitlines()
        else:
            finished_download = []

        def pdf_file_exists(converting=False):
            if replace and not converting:
                try:
                    delete_file(pdf_file)
                except FileNotFoundError:
                    pass
            return os.path.exists(pdf_file)

        if pdf_file_exists() and not exists_download and not replace:
            log.info("Chapter PDF file exist and replace is False, cancelling download...")
            return

        tracker_download = open(finished_download_path, "a" if exists_download else "w")

        # In case KeyboardInterrupt is called
        _cleanup_jobs.append(lambda: tracker_download.close())
        
        start = True
        for index, (vol, chap_class, images) in enumerate(cache):
            # Group name will be placed inside the start and end of chapter images
            chap = chap_class.chapter
            chap_name = chap_class.name

            log.info('Getting %s from chapter %s' % (
                'compressed images' if compressed_image else 'images',
                chap
            ))
            images.fetch()

            chapter_path = create_chapter_folder(base_path, chap_name)
            chapter_folders.append(chapter_path)

            while True:
                error = False
                for page, img_url, img_name in images.iter():
                    img_path = chapter_path / img_name

                    if not start:
                        img_name_manifest = str(img_path)
                    else:
                        img_name_manifest = 'start_%s' % chap_class.name
                    
                    if not start:
                        log.info('Downloading %s page %s' % (chap_name, page))

                    if img_name_manifest in finished_download and not self.replace:
                        imgs.append(Image.open(img_path))

                        if not start:
                            log.info("File exist and replace is False, cancelling download...")
                        continue

                    if not start:
                        downloader = ChapterPageDownloader(
                            img_url,
                            img_path,
                            replace=replace
                        )
                        success = downloader.download()
                    else:
                        success = True

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
                        if not start:
                            imgs.append(Image.open(img_path))
                        else:
                            imgs.append(
                                _ChapterMarkImage(
                                    get_mark_image,
                                    (chap_class, cache, index, start)
                                )
                            )
                            start = False

                        tracker_download.write(img_name_manifest + "\n")
                        tracker_download.flush()
                        continue
                
                if not error:
                    break

            # Insert end of chapter image
            imgs.append(_ChapterMarkImage(get_mark_image, (chap_class, cache, index, start)))

        log.info("Manga \"%s\" has finished download, converting to pdf..." % manga.title)

        pdf_plugin = PDFPlugin(imgs)

        # The first one image always be _ChapterMarkImage object
        start_img = imgs.pop(0)
        im = start_img.func(*start_img.args)

        # Convert it to PDF
        def save_pdf():
            im.save(
                pdf_file,
                save_all=True,
                append=True if pdf_file_exists(True) else False,
                append_images=imgs
            )

            # Close PDF convert progress bar
            pdf_plugin.close_progress_bar()

            # Cleaning up
            tracker_download.close()
            delete_file(finished_download_path)

            for folder in chapter_folders:
                shutil.rmtree(folder, ignore_errors=True)

        # Save it as pdf
        worker.submit(save_pdf)

        # Shutdown queue-based thread process
        worker.shutdown()
