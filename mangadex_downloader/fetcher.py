from requests.exceptions import HTTPError
from .errors import ChapterNotFound, HTTPException, InvalidManga, InvalidMangaDexList
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

def get_user(user_id):
    url = '{0}/user/{1}'.format(base_url, user_id)
    r = Net.requests.get(url)
    return r.json()

def get_cover_art(cover_id):
    url = '{0}/cover/{1}'.format(base_url, cover_id)
    r = Net.requests.get(url)
    return r.json()

def get_chapter(chapter_id):
    url = '{0}/chapter/{1}'.format(base_url, chapter_id)
    r = Net.requests.get(url)
    if r.status_code == 404:
        raise ChapterNotFound("Chapter %s cannot be found" % chapter_id)
    return r.json()

def get_list(list_id):
    url = '{0}/list/{1}'.format(base_url, list_id)
    r = Net.requests.get(url)
    if r.status_code == 404:
        raise InvalidMangaDexList("List %s cannot be found" % list_id)
    return r.json()

def get_group(group_id):
    url = '{0}/group/{1}'.format(base_url, group_id)
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