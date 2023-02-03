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

import re
import logging
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Union

from . import __repository__, __url_repository__
from .errors import InvalidURL, MangaDexException
from .network import Net, forums_url
from .utils import find_md_urls

log = logging.getLogger(__name__)

@dataclass
class _ResultValidationForumThreadURL:
    url: str
    thread_id: str
    page: Union[str, None]
    post_id: Union[str, None]

def get_post_id_forum_thread(url):
    post_id = None

    post_id_re = r"\/(#|)post-(?P<post_id>[0-9]+)"
    result = re.search(post_id_re, url)
    if result:
        post_id = result.group("post_id")
    
    return post_id

def validate_forum_thread_url(url):
    """Validate MangaDex forum thread url"""
    thread_id = None
    page = None

    # Find post id first
    post_id = get_post_id_forum_thread(url)

    # Then find full url 
    full_url_re = r"forums\.mangadex\.org\/threads\/(.{1,}\.|)(?P<thread_id>[0-9]+)(\/page-(?P<page>[0-9]+)|)"
    result = re.search(full_url_re, url)
    if result:
        try:
            thread_id = result.group("thread_id")
        except IndexError:
            # No forum thread id
            # hmmmm, sus
            raise InvalidURL(f"forum thread id from url '{url}' cannot be found")
        
        try:
            page = result.group("page")
        except IndexError:
            # No specific page number
            # it's okay, since it's optional
            pass

        return _ResultValidationForumThreadURL(
            url=url,
            thread_id=thread_id,
            page=page,
            post_id=post_id
        )
    
    # Check if it's numbers only
    # for forum thread id
    result = re.match(r"^[0-9]+$", url)
    if not result:
        # We cannot find thread forum id
        raise InvalidURL("Invalid forum thread URL")

    return _ResultValidationForumThreadURL(
        url=url,
        thread_id=result.group(),
        page=None,
        post_id=None
    )

def get_thread_title_owner_and_post_owner(parser=None, thread_url=None, post_id=None):
    post_owner = None

    if parser is None and thread_url:
        r = Net.mangadex.get(thread_url)
        parser = BeautifulSoup(r.text, "html.parser")

    # Finding thread owner
    thread_owner = parser.find("a", attrs={"class": ["username"], "data-xf-init": "member-tooltip"})
    if thread_owner is None:
        # Hmmmm, there is no thread owner in a forum thread ? sus
        raise MangaDexException(
            f"No thread owner in forum thread {thread_url}. " \
            f"Please report this issue to {__url_repository__}/{__repository__}/issues"
        )
    thread_owner = thread_owner.get_text(strip=True)

    # Finding thread title
    thread_title = parser.find("h1", attrs={"class": ["p-title-value"]})
    if thread_title is None:
        # No thread title ? VERY SUS
        raise MangaDexException(
            f"No thread title in forum thread {thread_url}. " \
            f"Please report this issue to {__url_repository__}/{__repository__}/issues"
        )
    thread_title = thread_title.get_text(strip=True)

    if post_id:
        article = parser.find("article", attrs={"data-content": f"post-{post_id}"})
        if article:
            post_owner = article.attrs["data-author"]

    return thread_title, thread_owner, post_owner

def get_absolute_forum_thread_url(result: _ResultValidationForumThreadURL):
    # Construct forum thread URL from forum thread ID
    url = f"{forums_url}/threads/{result.thread_id}"

    if result.post_id:
        url += f"/post-{result.post_id}"

    # The process is checking if the URL is gets redirected or not
    # if it's gets redirected the forum thread is exist
    # otherwise not
    r = Net.mangadex.get(url, allow_redirects=False)
    if r.is_redirect:
        result.url = r.headers.get("location")
    else:
        raise MangaDexException(f"forum thread id {result.thread_id} is not exist")

    return result

def iter_md_urls_from_forum_thread(url):
    min_page = None
    max_page = None
    next_pages = None

    # Check if it's containing the correct forums thread URL
    log.debug(f"Validating forum thread url = {url}")
    result = validate_forum_thread_url(url)

    # Make sure we get absolute forum thread URL
    result = get_absolute_forum_thread_url(result)

    # Let's begin the scrapping !
    r = Net.mangadex.get(result.url)
    parser = BeautifulSoup(r.text, "html.parser")

    thread_title, _, _ = get_thread_title_owner_and_post_owner(parser)

    # Check if it's has specific post id in URL
    if result.post_id is not None:
        article_post_id = parser.find("article", attrs={"data-content": f"post-{result.post_id}"})

        if article_post_id is not None:
            log.debug(f"Found post_id in forum thread url = {url}")
            log.debug(f"Finding MD urls from post id, instead of whole thread")
            # Begin iter MangaDex URLs
            for text in article_post_id.prettify().splitlines():
                result_url = find_md_urls(text)

                if result_url:
                    yield result_url
            
            return
        
        log.warning(
            f"Post id {result.post_id} cannot be found in forum thread '{thread_title}'. " \
            "Scanning URLs in whole thread"
        )

    # Check if there is another pages in forum thread
    ul_nav = parser.find("ul", attrs={"class": ["pageNav-main"]})
    if ul_nav is not None:
        next_pages_num = []

        # Get lowest and highest page numbers
        for link_nav in ul_nav.find_all("a"):
            link_nav_text = link_nav.decode_contents()
            if link_nav_text.isnumeric():
                next_pages_num.append(int(link_nav_text))

        # min_page = Current page
        min_page = min(next_pages_num) if result.page is None else result.page
        max_page = max(next_pages_num)

        # Because range() is starting at 0 
        # We need to check if it's same numbers as (min_page + 1) and max_page
        # to prevent range() is not returning value if it's same numbers
        min_page += 1
        if min_page == max_page:
            next_pages = range(min_page, max_page + 1)
        else:
            next_pages = range(min_page, max_page)
        
        log.debug(f"Found {max_page} pages in forum thread '{thread_title}'")

    def yield_urls_from_parser(parser):
        for element in parser.find_all("article", attrs={"class": ["message", "message--post"]}):
            for text in element.prettify().splitlines():
                result_url = find_md_urls(text)

                if result_url:
                    yield result_url

    # Yield urls from current page first
    current_page = (min_page - 1) if min_page is not None else result.page
    log.debug(f"Finding MD urls from page {current_page}")
    yield from yield_urls_from_parser(parser)

    if next_pages is None:
        return

    for page in next_pages:
        log.debug(f"Finding MD urls from page {page}")

        next_url = f"{forums_url}/threads/{result.thread_id}/page-{page}"
        r = Net.mangadex.get(next_url)
        next_parser = BeautifulSoup(r.text, "html.parser")

        yield from yield_urls_from_parser(next_parser)

        
