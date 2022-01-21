import logging
from pathvalidate import sanitize_filename
from pathlib import Path
from .utils import validate_url, write_details
from .utils import download as download_file
from .errors import InvalidURL
from .fetcher import *
from .manga import Manga
from .chapter import Chapter
from .downloader import ChapterPageDownloader

log = logging.getLogger(__name__)

__all__ = (
    'download',
)

def download(url, folder=None):
    log.debug('Validating the url...')
    try:
        manga_id = validate_url(url)
    except InvalidURL as e:
        log.error('%s is not valid mangadex url' % url)
        raise e from None
    
    # Begin fetching
    log.info('Fetching manga %s' % manga_id)
    data = get_manga(manga_id)

    # Append some additional informations
    rels = data['data']['relationships']
    author = None
    artist = None
    cover = None
    for rel in rels:
        _type = rel.get('type')
        _id = rel.get('id')
        if _type == 'author':
            author = _id
        elif _type == 'artist':
            artist = _id
        elif _type == 'cover_art':
            cover = _id

    log.debug('Getting author manga')
    data['author'] = get_author(author)

    log.debug('Getting artist manga')
    data['artist'] = get_author(artist)

    log.debug('Getting cover manga')
    data['cover_art'] = get_cover_art(cover)

    manga = Manga(data)

    # base path
    base_path = Path('.')

    # Extend the folder
    if folder:
        base_path /= folder
    base_path /= sanitize_filename(manga.title)
    
    # Create folder
    log.debug("Creating folder for downloading")
    base_path.mkdir(parents=True, exist_ok=True)

    # Cover path
    cover_path = base_path / 'cover.jpg'
    log.info('Downloading cover manga %s' % manga.title)
    download_file(manga.cover_art, str(cover_path))

    # Write details.json for tachiyomi local manga
    details_path = base_path / 'details.json'
    log.info('Writing details.json')
    write_details(manga, details_path)

    # Fetching chapters
    chapters = Chapter(get_all_chapters(manga.id))

    # Begin downloading
    for vol, chap, page, img_url, img_name in chapters.iter_chapter_images():
        # Create chapter folder
        chapter_folder = "" # type: str
        if vol != 'none':
            chapter_folder += 'Volume. %s ' % vol
        chapter_folder += 'Chapter. ' + chap
        
        chapter_path = base_path / chapter_folder
        if not chapter_path.exists():
            chapter_path.mkdir(exist_ok=True)

        img_path = chapter_path / img_name

        log.info('Downloading %s page %s' % (chapter_folder, page))
        downloader = ChapterPageDownloader(
            img_url,
            img_path
        )
        downloader.download()
    return manga