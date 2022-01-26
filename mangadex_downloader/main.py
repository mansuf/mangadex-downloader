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
from .network import Net

log = logging.getLogger(__name__)

__all__ = (
    'download', 'login', 'logout'
)

def login(*args, **kwargs):
    """Login to MangaDex

    Do not worry about token session, the library automatically handle this. 
    Login session will be automtically renewed (unless you called :meth:`logout()`).
    
    Parameters
    -----------
    password: :class:`str`
        Password to login
    username: Optional[:class:`str`]
        Username to login
    email: Optional[:class:`str`]
        Email to login
    
    Raises
    -------
    AlreadyLoggedIn
        User are already logged in
    ValueError
        Parameters are not valid
    InvalidLogin
        Login credential are not valid
    """
    Net.requests.login(*args, **kwargs)

def logout():
    """Logout from MangaDex
    
    Raises
    -------
    NotLoggedIn
        User are not logged in
    """
    Net.requests.logout()

def download(
    url,
    folder=None,
    compressed_image=False,
    start_chapter=None,
    end_chapter=None,
    no_oneshot_chapter=False
):
    # Validate start_chapter and end_chapter param
    if start_chapter is not None and not isinstance(start_chapter, float):
        raise ValueError("start_chapter must be float, not %s" % type(start_chapter))
    if end_chapter is not None and not isinstance(end_chapter, float):
        raise ValueError("end_chapter must be float, not %s" % type(end_chapter))

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
    for vol, chap, images in chapters.iter_chapter_images(
        start_chapter,
        end_chapter,
        no_oneshot_chapter,
        compressed_image
    ):
        # Fetching chapter images
        log.info('Getting %s from chapter %s' % (
            'compressed images' if compressed_image else 'images',
            chap
        ))
        images.fetch()

        # Create chapter folder
        chapter_folder = "" # type: str
        # Determine oneshot chapter
        if vol == 0 and chap == "none":
            chapter_folder += "Oneshot"
        elif vol == "none" and chap == "none":
            chapter_folder += "Oneshot"
        elif vol == "none" and chap == "0":
            chapter_folder += "Oneshot"
        else:
            if vol != 'none':
                chapter_folder += 'Volume. %s ' % vol
            chapter_folder += 'Chapter. ' + chap
        
        chapter_path = base_path / chapter_folder
        if not chapter_path.exists():
            chapter_path.mkdir(exist_ok=True)

        while True:
            error = False
            for page, img_url, img_name in images.iter():
                img_path = chapter_path / img_name

                log.info('Downloading %s page %s' % (chapter_folder, page))
                downloader = ChapterPageDownloader(
                    img_url,
                    img_path
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
                
    log.info("Download finished for manga \"%s\"" % manga.title)
    return manga