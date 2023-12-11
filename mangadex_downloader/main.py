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
import re
from .errors import UnhandledException, MangaDexException
from .utils import (
    comma_separated_text,
    create_directory,
    check_blacklisted_tags_manga,
    get_cover_art_url,
)
from .language import Language, get_language
from .fetcher import get_legacy_id
from .iterator import CoverArtIterator
from .mdlist import MangaDexList
from .manga import Manga
from .chapter import Chapter
from .format import get_format
from .downloader import FileDownloader
from .config import config
from .tracker import get_tracker
from .path.op import get_path

log = logging.getLogger(__name__)


def download(
    manga_id,
    replace=False,
    start_chapter=None,
    end_chapter=None,
    start_page=None,
    end_page=None,
    no_oneshot_chapter=False,
    use_alt_details=False,
    groups=None,
    _range=None,
):
    """Download a manga"""
    save_as = config.save_as
    cover = config.cover

    lang = get_language(config.language)

    log.info(f"Using {lang.name} language")

    # Validation save as format
    fmt_class = get_format(save_as)

    manga = Manga(_id=manga_id, use_alt_details=use_alt_details)

    # Check blacklisted tags in manga
    blacklisted, tags = check_blacklisted_tags_manga(manga)

    if blacklisted:
        log.warning(
            f"Not downloading manga '{manga.title}', "
            f"since it contain one or more blacklisted tags {tags}"
        )
        return manga

    all_languages = lang == Language.All

    if not all_languages:
        log.info("Fetching all chapters...")
        manga.fetch_chapters(lang.value, all_chapters=True)

    # Reuse is good
    def download_manga(m, path):
        kwargs_iter_chapter_images = {
            "start_chapter": start_chapter,
            "end_chapter": end_chapter,
            "start_page": start_page,
            "end_page": end_page,
            "no_oneshot": no_oneshot_chapter,
            "groups": groups,
            "_range": _range,
        }

        log.info("Using %s format" % save_as)

        # Cover path
        cover_path = path / "cover.jpg"
        log.info("Downloading cover manga %s" % manga.title)

        # Determine cover art quality
        cover_url = get_cover_art_url(manga.id, manga.cover, cover)

        # Download the cover art
        if cover == "none":
            log.info('Not downloading cover manga, since "cover" is none')
        elif cover_url is None:
            # The manga doesn't have cover
            log.info(
                "Not downloading cover manga, "
                f"since manga '{manga.title}' doesn't have cover"
            )
        else:
            fd = FileDownloader(
                cover_url,
                cover_path,
                replace=replace,
            )
            fd.download()
            fd.cleanup()

        m.tracker = get_tracker(save_as, path)

        fmt = fmt_class(path, m, replace, kwargs_iter_chapter_images)

        # Execute main format
        fmt.main()

    if all_languages:
        # Print info to users
        # Let the users know how many translated languages available
        # in given manga
        translated_langs = [i.name for i in manga.translated_languages]
        log.info(
            f"Available translated languages = {comma_separated_text(translated_langs)}"
        )

        for translated_lang in manga.translated_languages:
            log.info(f"Downloading {manga.title} in {translated_lang.name} language")

            # Copy title and description manga
            new_manga = Manga(data=manga._data)
            new_manga._title = manga.title
            new_manga._description = manga.description

            # Fetch all chapters
            new_manga.fetch_chapters(translated_lang.value, all_chapters=True)

            formatted_path = create_directory("", get_path(new_manga))
            log.info(f'Download directory is set to "{formatted_path.resolve()}"')
            download_manga(new_manga, formatted_path)

            log.info(
                f"Download finished for manga {manga.title} "
                f"in {translated_lang.name} language"
            )

    else:
        formatted_path = create_directory("", get_path(manga))
        log.info(f'Download directory is set to "{formatted_path.resolve()}"')
        download_manga(manga, formatted_path)

    log.info('Download finished for manga "%s"' % manga.title)
    return manga


def download_chapter(
    chap_id,
    replace=False,
    start_page=None,
    end_page=None,
):
    """Download a chapter"""
    save_as = config.save_as
    fmt_class = get_format(save_as)

    # Fetch manga
    chap = Chapter(chap_id)
    manga = Manga(_id=chap.manga_id)
    manga.fetch_chapters(chap.language.value, chap)

    log.info(f'Found chapter {chap.chapter} from manga "{manga.title}"')

    # Create folder for downloading
    base_path = create_directory(manga.title, config.path)
    log.info(f'Download directory is set to "{base_path.resolve()}"')

    kwargs_iter_chapter_images = {
        "start_page": start_page,
        "end_page": end_page,
        "no_oneshot": False,
    }

    log.info(f"Using {save_as} format")
    manga.tracker = get_tracker(save_as, base_path)

    fmt = fmt_class(base_path, manga, replace, kwargs_iter_chapter_images)

    # Execute main format
    fmt.main()

    log.info(f'Finished download chapter {chap.chapter} from manga "{manga.title}"')
    return manga


def download_list(
    list_id,
    replace=False,
    groups=None,
):
    """Download a list"""
    _list = MangaDexList(_id=list_id)

    for manga in _list.iter_manga():
        download(
            manga.id,
            replace,
            groups=groups,
        )


def download_legacy_manga(legacy_id, *args, **kwargs):
    """Download manga from old MangaDex url

    The rest of parameters will be passed to :meth:`download`.
    """
    # Mark it as deprecated
    # bye bye :(
    log.warning(
        "Old MangaDex URL are deprecated and will be removed any time soon. "
        "Please use the new MangaDex URL"
    )

    new_id = get_legacy_id("manga", legacy_id)
    manga = download(new_id, *args, **kwargs)
    return manga


def download_legacy_chapter(legacy_id, *args, **kwargs):
    """Download chapter from old MangaDex url

    The rest of parameters will be passed to :meth:`download_chapter`
    """
    # Mark it as deprecated
    # bye bye :(
    log.warning(
        "Old MangaDex URL are deprecated and will be removed any time soon. "
        "Please use the new MangaDex URL"
    )

    new_id = get_legacy_id("chapter", legacy_id)
    manga = download_chapter(new_id, *args, **kwargs)
    return manga


def download_cover_art_manga(url, replace=False):
    # This is hack actually
    # Since the covers URL are not including cover id
    # (https://mangadex.org/covers/{manga_id}/{filename})
    # We gonna find filename cover in list of covers
    log.info("Getting manga id from cover url")
    regex = (
        r".+(mangadex\.org|uploads\.mangadex\.org)\/covers\/"
        r"(?P<manga_id>[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})\/"
        r"(?P<filename>[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\.[a-zA-Z]{1,}.+)"
    )
    result = re.search(regex, url)
    if result is None:
        raise UnhandledException(f"Cannot find manga id in cover URL = {url}")

    log.info("Finding matching cover from filename")
    iterator = CoverArtIterator(result.group("manga_id"))
    cover = None
    filename = result.group("filename")

    for cv in iterator:
        if cv.file in filename:
            cover = cv
            break

    if cover is None:
        raise MangaDexException(f"Cannot find matching cover from filename {filename}")

    manga = Manga(_id=cover.manga_id)
    if cover.volume is None:
        cover_name = "No volume cover"
    else:
        cover_name = f"Volume {cover.volume} cover"
    log.info(f"Found {cover_name} from '{manga.title}', downloading...")

    # Merge file ext with new filename
    _, file_ext = filename.split(".", maxsplit=1)
    filename = cover_name + "." + file_ext
    base_path = create_directory(manga.title, path=config.path)
    path = base_path / filename
    log.info(f"Download directory is set to {base_path}")

    def handle_error(err, resp):
        if not resp.ok:
            filename = result.group("filename")
            raise MangaDexException(f"Cover file '{filename}' is not found on MangaDex")

    log.info(f"Downloading file '{filename}'")
    fd = FileDownloader(url=url, file=path, replace=replace)
    fd.on_error = handle_error
    fd.download()
    fd.cleanup()
