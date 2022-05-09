import logging
from pathvalidate import sanitize_filename
from pathlib import Path
from .utils import (
    validate_group_url,
    validate_legacy_url,
    validate_url, 
    valid_cover_types,
    default_cover_type
)
from .language import Language, get_language
from .utils import download as download_file
from .errors import InvalidURL
from .fetcher import *
from .manga import IteratorManga, Manga
from .chapter import Chapter, MangaChapter
from .network import Net
from .format import default_save_as_format, get_format
from .artist_and_author import Artist, Author
from .cover import CoverArt

log = logging.getLogger(__name__)

__all__ = (
    'download', 'download_chapter', 'download_list',
    'fetch', 'login', 'logout', 'search'
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
    LoginFailed
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

def _get_manga_from_chapter(chapter_id):
    chap = Chapter(chapter_id)
    manga = _fetch_manga(chap.manga_id, chap.language.value, fetch_all_chapters=False)
    manga._chapters = MangaChapter(manga, chap.language.value, chap)
    return chap, manga

def _fetch_manga(
    manga_id,
    lang,
    fetch_all_chapters=True,
    use_alt_details=False
):
    manga = Manga(_id=manga_id, use_alt_details=use_alt_details)

    if fetch_all_chapters:
        # NOTE: After v0.4.0, fetch the chapters first before creating folder for downloading the manga
        # and downloading the cover manga.
        # This will check if selected language in manga has chapters inside of it.
        # If the chapters are not available, it will throw error.
        log.info("Fetching all chapters...")
        chapters = MangaChapter(manga, lang, all_chapters=True)
        manga._chapters = chapters

    return manga

def search(*args, **kwargs):
    """Search manga

    Parameters
    -----------
    title: :class:`str`
        Manga title

    Returns
    --------
    :class:`IteratorManga`
        An iterator that yield :class:`Manga`
    """
    return IteratorManga(*args, **kwargs)

def fetch(url, language=Language.English, use_alt_details=False):
    """Fetch the manga

    Parameters
    -----------
    url: :class:`str`
        A MangaDex URL or manga id
    language: :class:`Language` (default: :class:`Language.English`)
        Select a translated language for manga

    Raises
    -------
    InvalidURL
        Not a valid MangaDex url
    InvalidManga
        Given manga cannot be found
    ChapterNotFound
        Given manga has no chapters

    Returns
    --------
    :class:`Manga`
        An fetched manga
    """
    # Parse language
    if isinstance(language, Language):
        lang = language.value
    elif isinstance(language, str):
        lang = get_language(language).value
    else:
        raise ValueError("language must be Language or str, not %s" % language.__class__.__name__)
    log.info("Using %s language" % Language(lang).name)

    log.debug('Validating the url...')
    try:
        manga_id = validate_url(url)
    except InvalidURL as e:
        log.error('%s is not valid mangadex url' % url)
        raise e from None
    
    # Begin fetching
    log.info('Fetching manga %s' % manga_id)
    manga = _fetch_manga(manga_id, lang, use_alt_details=use_alt_details)
    log.info("Found manga \"%s\"" % manga.title)

    return manga

def download(
    url,
    folder=None,
    replace=False,
    compressed_image=False,
    start_chapter=None,
    end_chapter=None,
    start_page=None,
    end_page=None,
    no_oneshot_chapter=False,
    language=Language.English,
    cover=default_cover_type,
    save_as=default_save_as_format,
    use_alt_details=False,
    no_group_name=False,
    group=None,
    legacy_sorting=False,
    use_chapter_title=False
):
    """Download a manga
    
    Parameters
    -----------
    url: :class:`str`
        A MangaDex URL or manga id. It also accepting :class:`Manga` object
    folder: :class:`str` (default: ``None``)
        Store manga in given folder
    replace: :class:`bool` (default: ``False``)
        Replace manga if exist
    compressed_image: :class:`bool` (default: ``False``)
        Use compressed images for low size when downloading manga
    start_chapter: :class:`float` (default: ``None``)
        Start downloading manga from given chapter
    end_chapter: :class:`float` (default: ``None``)
        Stop downloading manga from given chapter
    start_page: :class:`int` (default: ``None``)
        Start download chapter page from given page number
    end_page: :class:`int` (default: ``None``)
        Stop download chapter page from given page number
    no_oneshot_manga: :class:`bool` (default: ``False``)
        If exist, don\'t download oneshot chapter
    language: :class:`Language` (default: :class:`Language.English`)
        Select a translated language for manga
    cover: :class:`str` (default: ``original``)
        Choose quality cover manga
    save_as: :class:`str` (default: ``tachiyomi``)
        Choose save as format
    use_alt_details: :class:`bool` (default: ``False``)
        Use alternative title and description manga
    no_group_name: :class:`bool` (default: ``False``)
        If ``True``, Do not use scanlation group name for each chapter.
    group: :class:`str` (default: ``None``)
        Use different scanlation group for each chapter.
    legacy_sorting: :class:`bool` (default: ``False``)
        if ``True``, Enable legacy sorting chapter images for old reader application.
    use_chapter_title: :class:`bool` (default: ``False``)
        If ``True``, use chapter title for each chapters.
        NOTE: This option is useless if used with any single format.

    Raises
    -------
    InvalidURL
        Not a valid MangaDex url
    InvalidManga
        Given manga cannot be found
    ChapterNotFound
        Given manga has no chapters

    Returns
    --------
    :class:`Manga`
        An downloaded manga
    """
    # Validate start_chapter and end_chapter param
    if start_chapter is not None and not isinstance(start_chapter, float):
        raise ValueError("start_chapter must be float, not %s" % type(start_chapter))
    if end_chapter is not None and not isinstance(end_chapter, float):
        raise ValueError("end_chapter must be float, not %s" % type(end_chapter))

    if start_chapter is not None and end_chapter is not None:
        if start_chapter > end_chapter:
            raise ValueError("start_chapter cannot be more than end_chapter")

    if start_page is not None and end_page is not None:
        if start_page > end_page:
            raise ValueError("start_page cannot be more than end_page")

    if cover not in valid_cover_types:
        raise ValueError("invalid cover type, available are: %s" % valid_cover_types)

    if group and group.lower().strip() == "all" and no_group_name:
        raise ValueError("no_group_name cannot be True while group is used")

    # Validate group
    group_id = validate_group_url(group)

    # Validation save as format
    fmt_class = get_format(save_as)

    if not isinstance(url, Manga):
        manga = fetch(url, language, use_alt_details)
    else:
        manga = url

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

    # Determine cover art quality
    if cover == "original":
        cover_url = manga.cover_art
    elif cover == "512px":
        cover_url = manga.cover_art_512px
    elif cover == "256px":
        cover_url = manga.cover_art_256px
    elif cover == 'none':
        cover_url = None

    # Download the cover art
    if cover_url is None:
        log.debug('Not downloading cover manga, since \"cover\" is none')
    else:
        download_file(cover_url, str(cover_path), replace=True)

    kwargs_iter_chapter_images = {
        "start_chapter": start_chapter,
        "end_chapter": end_chapter,
        "start_page": start_page,
        "end_page": end_page,
        "no_oneshot": no_oneshot_chapter,
        "data_saver": compressed_image,
        "no_group_name": no_group_name,
        "group": group_id,
        "use_chapter_title": use_chapter_title
    }

    log.info("Using %s format" % save_as)

    fmt = fmt_class(
        base_path,
        manga,
        compressed_image,
        replace,
        legacy_sorting,
        kwargs_iter_chapter_images
    )

    # Execute main format
    fmt.main()
                
    log.info("Download finished for manga \"%s\"" % manga.title)
    return manga

def download_chapter(
    url,
    folder=None,
    replace=False,
    start_page=None,
    end_page=None,
    compressed_image=False,
    save_as=default_save_as_format,
    no_group_name=False,
    legacy_sorting=False,
    use_chapter_title=False
):
    """Download a chapter
    
    Parameters
    -----------
    url: :class:`str`
        A MangaDex URL or chapter id
    folder: :class:`str` (default: ``None``)
        Store chapter manga in given folder
    replace: :class:`bool` (default: ``False``)
        Replace chapter manga if exist
    start_page: :class:`int` (default: ``None``)
        Start download chapter page from given page number
    end_page: :class:`int` (default: ``None``)
        Stop download chapter page from given page number
    compressed_image: :class:`bool` (default: ``False``)
        Use compressed images for low size when downloading chapter manga
    save_as: :class:`str` (default: ``tachiyomi``)
        Choose save as format
    no_group_name: :class:`bool` (default: ``False``)
        If ``True``, Do not use scanlation group name for each chapter.
    legacy_sorting: :class:`bool` (default: ``False``)
        if ``True``, Enable legacy sorting chapter images for old reader application.
    use_chapter_title: :class:`bool` (default: ``False``)
        If ``True``, use chapter title for each chapters.
        NOTE: This option is useless if used with any single format.

    Returns
    --------
    :class:`Manga`
        An :class:`Manga` that has this chapter
    """
    # Validate start_page and end_page param
    if start_page is not None and not isinstance(start_page, int):
        raise ValueError("start_page must be int, not %s" % type(start_page))
    if end_page is not None and not isinstance(end_page, int):
        raise ValueError("end_page must be int, not %s" % type(end_page))

    if start_page is not None and end_page is not None:
        if start_page > end_page:
            raise ValueError("start_page cannot be more than end_page")

    fmt_class = get_format(save_as)

    log.debug('Validating the url...')
    try:
        chap_id = validate_url(url)
    except InvalidURL as e:
        log.error('%s is not valid mangadex url' % url)
        raise e from None

    # Fetch manga
    chap, manga = _get_manga_from_chapter(chap_id)
    log.info("Found chapter %s from manga \"%s\"" % (chap.chapter, manga.title))

    # base path
    base_path = Path('.')

    # Extend the folder
    if folder:
        base_path /= folder
    base_path /= sanitize_filename(manga.title)
    
    # Create folder
    log.debug("Creating folder for downloading")
    base_path.mkdir(parents=True, exist_ok=True)

    kwargs_iter_chapter_images = {
        "start_page": start_page,
        "end_page": end_page,
        "no_oneshot": False,
        "data_saver": compressed_image,
        "no_group_name": no_group_name,
        "use_chapter_title": use_chapter_title
    }

    log.info("Using %s format" % save_as)

    fmt = fmt_class(
        base_path,
        manga,
        compressed_image,
        replace,
        legacy_sorting,
        kwargs_iter_chapter_images
    )

    # Execute main format
    fmt.main()

    log.info("Finished download chapter %s from manga \"%s\"" % (chap.chapter, manga.title))
    return manga

def download_list(
    url,
    folder=None,
    replace=False,
    compressed_image=False,
    language=Language.English,
    cover=default_cover_type,
    save_as=default_save_as_format,
    no_group_name=False,
    group=None,
    legacy_sorting=False,
    use_chapter_title=True
):
    """Download a list

    Parameters
    -----------
    url: :class:`str`
        A MangaDex URL or chapter id
    folder: :class:`str` (default: ``None``)
        Store chapter manga in given folder
    replace: :class:`bool` (default: ``False``)
        Replace chapter manga if exist
    compressed_image: :class:`bool` (default: ``False``)
        Use compressed images for low size when downloading chapter manga
    save_as: :class:`str` (default: ``tachiyomi``)
        Choose save as format
    no_group_name: :class:`bool` (default: ``False``)
        If ``True``, Do not use scanlation group name for each chapter.
    group: :class:`str` (default: ``None``)
        Use different scanlation group for each chapter.
    legacy_sorting: :class:`bool` (default: ``False``)
        if ``True``, Enable legacy sorting chapter images for old reader application.
    use_chapter_title: :class:`bool` (default: ``False``)
        If ``True``, use chapter title for each chapters.
        NOTE: This option is useless if used with any single format.
    """
    log.debug('Validating the url...')
    try:
        list_id = validate_url(url)
    except InvalidURL as e:
        log.error('%s is not valid mangadex url' % url)
        raise e from None

    data = get_list(list_id)
    name = data['data']['attributes']['name']
    rels = data['data']['relationships']

    # Get list of mangas
    mangas_id = []
    for rel in rels:
        _id = rel['id']
        _type = rel['type']
        if _type == "manga":
            manga = _fetch_manga(_id, "en", fetch_all_chapters=False)
            log.info("Found \"%s\" manga from \"%s\" list" % (manga.title, name))
            mangas_id.append(_id)

    for manga_id in mangas_id:
        download(
            manga_id,
            folder,
            replace,
            compressed_image,
            cover=cover,
            save_as=save_as,
            language=language,
            no_group_name=no_group_name,
            group=group,
            legacy_sorting=legacy_sorting,
            use_chapter_title=use_chapter_title
        )

def download_legacy_manga(url, *args, **kwargs):
    """Download manga from old MangaDex url
    
    The rest of parameters will be passed to :meth:`download`.
    """
    log.debug('Validating the url...')
    try:
        legacy_id = validate_legacy_url(url)
    except InvalidURL as e:
        log.error('%s is not valid mangadex url' % url)
        raise e from None

    new_id = get_legacy_id('manga', legacy_id)

    manga = download(new_id, *args, **kwargs)
    return manga

def download_legacy_chapter(url, *args, **kwargs):
    """Download chapter from old MangaDex url
    
    The rest of parameters will be passed to :meth:`download_chapter`
    """
    log.debug('Validating the url...')
    try:
        legacy_id = validate_legacy_url(url)
    except InvalidURL as e:
        log.error('%s is not valid mangadex url' % url)
        raise e from None

    new_id = get_legacy_id('chapter', legacy_id)

    manga = download_chapter(new_id, *args, **kwargs)
    return manga