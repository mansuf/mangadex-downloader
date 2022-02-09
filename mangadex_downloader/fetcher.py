from requests.exceptions import HTTPError
from .errors import HTTPException, InvalidManga
from .network import Net, base_url

def get_manga(manga_id):
    url = '{0}/manga/{1}'.format(base_url, manga_id)
    r = Net.requests.get(url)
    if r.status_code == 404:
        raise InvalidManga('Manga \"%s\" cannot be found' % manga_id)
    return r.json()

def get_author(author_id):
    url = '{0}/author/{1}'.format(base_url, author_id)
    r = Net.requests.get(url)
    return r.json()

def get_cover_art(cover_id):
    url = '{0}/cover/{1}'.format(base_url, cover_id)
    r = Net.requests.get(url)
    return r.json()

def get_chapter(chapter_id):
    url = '{0}/chapter/{1}'.format(base_url, chapter_id)
    r = Net.requests.get(url)
    return r.json()

def get_all_chapters(manga_id, lang):
    url = '{0}/manga/{1}/aggregate'.format(base_url, manga_id)
    r = Net.requests.get(url, params={'translatedLanguage[]': [lang]})
    return r.json()

def get_chapter_images(chapter_id):
    url = '{0}/at-home/server/{1}'.format(base_url, chapter_id)
    r = Net.requests.get(url)
    return r.json()