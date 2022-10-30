import os
import zipfile
import shutil
import tqdm
import logging
from pathvalidate import sanitize_filename
from .base import BaseFormat
from .utils import NumberWithLeadingZeros, get_chapter_info

from ..utils import create_directory, delete_file
from ..errors import MangaDexException

class EpubMissingDependencies(MangaDexException):
    """Raised when `lxml` and `bs4` is not installed"""
    def __init__(self, *args, **kwargs):
        super().__init__("`lxml`, `bs4` and `Pillow` is not installed")

try:
    import lxml
    from bs4 import BeautifulSoup, Doctype, Comment
    from PIL import Image
except ImportError:
    epub_ready = False
else:
    epub_ready = True

log = logging.getLogger(__name__)

# Inspired from https://github.com/manga-download/hakuneko/blob/master/src/web/mjs/engine/EbookGenerator.mjs
# TODO: Add doc for this class
class EpubPlugin:
    def __init__(self, _id, title, lang):
        self.id = _id
        self.title = title
        self.lang = lang

        self._pos = 0
        self._pages = {}

        # Container.xml
        self._container = None
        self._make_container()

        # for .opf document
        self._opf_root = None
        self._manifest = None
        self._spine = None
        self._make_opf()

        # toc.ncx
        self._toc_root = None
        self._navigation = None
        self._make_toc()

    def _make_toc(self):
        root = self._get_root()
        self._toc_root = root

        # <ncx>
        ncx = root.new_tag(
            'ncx',
            attrs={
                'xmlns': 'http://www.daisy.org/z3986/2005/ncx/',
                'version': '2005-1',
                "xmlns:ncx": "http://www.daisy.org/z3986/2005/ncx/",
            }
        )
        root.append(ncx)

        # <head>
        head = root.new_tag('head')
        meta_tag = root.new_tag(
            'meta',
            attrs={
                'name': 'dtb:uid',
                'content': self.id
            }
        )
        head.append(meta_tag)
        ncx.append(head)

        # <docTitle>
        doc_title = root.new_tag('docTitle')
        text_tag = root.new_tag('text')
        text_tag.string = self.title
        doc_title.append(text_tag)
        ncx.append(doc_title)

        # <navMap>
        nav = root.new_tag('navMap')
        ncx.append(nav)
        self._navigation = nav

    def _make_opf(self):
        root = self._get_root()
        self._opf_root = root

        package = root.new_tag(
            'package',
            attrs={
                'xmlns': 'http://www.idpf.org/2007/opf',
                'unique-identifier': self.id,
                'version': '2.0'
            }
        )
        root.append(package)

        # <metadata>
        metadata = root.new_tag(
            'metadata',
            attrs={
                'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
                'xmlns:opf': 'http://www.idpf.org/2007/opf'
            }
        )
        dc_title = root.new_tag('dc:title')
        dc_title.string = self.title
        dc_language = root.new_tag('dc:language')
        dc_language.string = self.lang
        dc_id = root.new_tag(
            'dc:identifier',
            attrs={
                'id': self.id,
                'opf:scheme': 'UUID'
            }
        )
        dc_id.string = self.id
        metadata.append(dc_title)
        metadata.append(dc_language)
        metadata.append(dc_id)
        package.append(metadata)

        # <manifest>
        manifest = root.new_tag('manifest')
        ncx_tag = root.new_tag(
            'item',
            attrs={
                'id': 'ncx',
                'href': 'toc.ncx',
                'media-type': 'application/x-dtbncx+xml'
            }
        )
        manifest.append(ncx_tag)
        package.append(manifest)
        self._manifest = manifest

        # <spine>
        spine = root.new_tag('spine', attrs={'toc': 'ncx'})
        package.append(spine)
        self._spine = spine

    def _get_root(self):
        return BeautifulSoup("", "xml")

    def _create_nav(self, _id, text, src=None):
        navpoint_kwargs = {
            'id': _id,
        }

        toc = self._toc_root.new_tag(
            'navPoint',
            attrs=navpoint_kwargs
        )
        toc_label = self._toc_root.new_tag('navLabel')
        toc_text = self._toc_root.new_tag('text')
        toc_text.string = text
        toc_label.append(toc_text)
        toc.append(toc_label)

        if src:
            toc_content = self._toc_root.new_tag(
                'content',
                attrs={
                    'src': src
                }
            )
            toc.append(toc_content)
        
        return toc

    def _create_toc_item(self, nav, path, pos):
        xhtml_path = f'xhtml/{path}_{pos}.xhtml'
        nav_point = self._create_nav(
            f'TOC_{path}_{pos}',
            f'Page {pos}',
            xhtml_path
        )
        nav.append(nav_point)

    def _create_manifest_item(self, path, pos, image):
        im_name = os.path.basename(image)
        im = Image.open(image)

        xhtml_item = self._opf_root.new_tag(
            'item',
            attrs={
                'id': f'XHTML_{path}_{pos}',
                'href': f'xhtml/{path}_{pos}.xhtml',
                'media-type': 'application/xhtml+xml'
            }
        )
        img_item = self._opf_root.new_tag(
            'item',
            attrs={
                'id': f'IMAGES_{path}_{pos}',
                'href': f'images/{path}_{im_name}',
                'media-type': Image.MIME.get(im.format)
            }
        )
        im.close()

        self._manifest.append(xhtml_item)
        self._manifest.append(img_item)

    def _create_spine_item(self, path, pos):
        item = self._opf_root.new_tag(
            'itemref',
            attrs={
                'idref': f'XHTML_{path}_{pos}'
            }
        )
        self._spine.append(item)

    def create_page(self, title, images):
        # Create page toc
        nav = self._create_nav(
            f"TOC_{self._pos}_INIT",
            title,
            f"xhtml/{self._pos}_1.xhtml"
        )
        xhtml = []

        for pos, im in enumerate(images, start=1):
            image = os.path.basename(im)
            root = self._get_root()

            # Make doctype
            doctype = Doctype.for_name_and_ids(
                "html",
                '-//W3C//DTD XHTML 1.1//EN',
                'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'
            )
            root.append(doctype)

            html_root = root.new_tag(
                'html',
                attrs={
                    'xmlns': 'http://www.w3.org/1999/xhtml'
                }
            )

            # Head document
            head_root = root.new_tag('head')
            title_tag = root.new_tag('title')
            title_tag.string = title
            head_root.append(title_tag)

            # Body document
            body_root = root.new_tag('body')
            div_tag = root.new_tag('div')
            img_tag = root.new_tag(
                'img',
                attrs={
                    'alt': image,
                    'src': f'../images/{self._pos}_{image}',
                }
            )
            div_tag.append(img_tag)
            body_root.append(div_tag)

            # HTML root
            html_root.append(head_root)
            html_root.append(body_root)
            root.append(html_root)

            self._create_manifest_item(self._pos, pos, im)
            self._create_spine_item(self._pos, pos)
            self._create_toc_item(nav, self._pos, pos)

            xhtml.append(root)

        self._navigation.append(nav)

        self._pages[self._pos] = [
            xhtml,
            images
        ]

        self._pos += 1

    def _make_container(self):
        root = self._get_root()
        container_tag = root.new_tag(
            "container",
            attrs={
                "version": "1.0",
                "xmlns": "urn:oasis:names:tc:opendocument:xmlns:container"
            }
        )
        rootfiles_tag = root.new_tag("rootfiles")
        rootfile_tag = root.new_tag(
            "rootfile",
            attrs={
                "full-path": "OEBPS/content.opf",
                "media-type": "application/oebps-package+xml"
            }
        )

        rootfiles_tag.append(rootfile_tag)
        container_tag.append(rootfiles_tag)
        root.append(container_tag)

        self._container = root
    
    def write(self, path):
        from ..config import env, config

        progress_bar = tqdm.tqdm(
            total=len(self._pages),
            initial=0,
            desc='epub_progress',
            unit='item',
            disable=config.no_progress_bar
        )

        with zipfile.ZipFile(
            path, 
            "a" if os.path.exists(path) else "w",
            compression=env.zip_compression_type,
            compresslevel=env.zip_compression_level
        ) as zip_obj:
            # Write MIMETYPE
            zip_obj.writestr('mimetype', 'application/epub+zip')

            # Write container
            zip_obj.writestr('META-INF/container.xml', self._container.prettify())

            # Write table of contents
            zip_obj.writestr('OEBPS/toc.ncx', str(self._toc_root))

            # Write .opf document
            zip_obj.writestr('OEBPS/content.opf', self._opf_root.prettify())

            # Write XHTML and images
            for page, (xhtml, images) in self._pages.items():

                for pos, content in enumerate(xhtml, start=1):
                    zip_obj.writestr(f'OEBPS/xhtml/{page}_{pos}.xhtml', content.prettify())

                for pos, image in enumerate(images, start=1):
                    zip_obj.write(
                        image, 
                        f'OEBPS/images/{page}_{os.path.basename(image)}'
                    )

                progress_bar.update(1)

class Epub(BaseFormat):
    def __init__(self, *args, **kwargs):
        if not epub_ready:
            raise EpubMissingDependencies()
        
        super().__init__(*args, **kwargs)

    def convert(self, _id, title, lang, chapters, path):
        epub = EpubPlugin(_id, title, lang)

        for chapter, images in chapters:
            epub.create_page(chapter.get_name(), images)
        
        epub.write(path)

    def main(self):
        manga = self.manga
        worker = self.create_worker()

        # Begin downloading
        for chap_class, images in manga.chapters.iter(**self.kwargs_iter):
            chap_name = chap_class.get_simplified_name()

            # Check if .epub file is exist or not
            chapter_epub_path = self.path / (chap_name + '.epub')
            if chapter_epub_path.exists():

                if self.replace:
                    delete_file(chapter_epub_path)
                else:
                    log.info(f"'{chapter_epub_path.name}' is exist and replace is False, cancelling download...")
                    continue

            chapter_path = create_directory(chap_name, self.path)

            count = NumberWithLeadingZeros(chap_class.pages)
            images = self.get_images(chap_class, images, chapter_path, count)

            log.info(f"{chap_name} has finished download, converting to epub...")

            # KeyboardInterrupt safe
            job = lambda: self.convert(
                manga.id,
                manga.title,
                chap_class.language.value,
                [(chap_class, images)],
                chapter_epub_path
            )
            worker.submit(job)

            # Remove original chapter folder
            shutil.rmtree(chapter_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class EpubVolume(Epub):
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
            epub_chapters = []

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

            volume_epub_path = self.path / (volume + '.epub')

            # Check if exist or not
            if volume_epub_path.exists():
                
                if self.replace:
                    delete_file(volume_epub_path)
                else:
                    log.info(f"{volume_epub_path.name} is exist and replace is False, cancelling download...")
                    continue

            # Create volume folder
            volume_path = create_directory(volume, self.path)

            for chap_class, chap_images in chapters:
                images = []
                images.extend(self.get_images(chap_class, chap_images, volume_path, count))
                epub_chapters.append((chap_class, images))

            log.info(f"{volume} has finished download, converting to epub...")

            job = lambda: self.convert(
                manga.id,
                manga.title,
                manga.chapters.language.value,
                epub_chapters,
                volume_epub_path
            )
            worker.submit(job)
                
            # Remove original chapter folder
            shutil.rmtree(volume_path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()

class EpubSingle(Epub):
    def main(self):
        epub_chapters = []
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
        manga_epub_path = self.path / (merged_name + '.epub')

        # Check if exist or not
        if manga_epub_path.exists():
            if self.replace:
                delete_file(manga_epub_path)
            else:
                log.info(f"{manga_epub_path.name} is exist and replace is False, cancelling download...")
                return

        path = create_directory(merged_name, self.path)

        for chap_class, chap_images in cache:
            images = []
            # Begin downloading
            images.extend(self.get_images(chap_class, chap_images, path, count))

            epub_chapters.append((chap_class, images))

        # Convert
        log.info(f"Manga '{manga.title}' has finished download, converting to epub...")

        job = lambda: self.convert(
            manga.id,
            manga.title,
            manga.chapters.language.value,
            epub_chapters,
            manga_epub_path
        )
        worker.submit(job)

        # Remove downloaded images
        shutil.rmtree(path, ignore_errors=True)

        # Shutdown queue-based thread process
        worker.shutdown()
