import argparse
import os
import sys

from .utils import Paginator
from .url import build_URL_from_type, smart_select_url
from ..network import Net
from ..main import search, get_manga_from_user_library
from ..utils import (
    validate_url as __validate,
    validate_legacy_url,
    input_handle
)
from ..errors import InvalidURL, MangaDexException

def _validate(url):
    try:
        _url = __validate(url)
    except InvalidURL:
        pass
    else:
        return _url
    # Legacy support
    try:
        _url = validate_legacy_url(url)
    except InvalidURL as e:
        raise argparse.ArgumentTypeError(str(e))
    return _url

def validate_url(url):
    if os.path.exists(url):
        with open(url, 'r') as opener:
            content = opener.read()
    else:
        content = url

    urls = []
    for _url in content.splitlines():
        if not _url:
            continue

        urls.append((_validate(_url), _url))
    
    return urls

def _create_prompt_choices(
    parser,
    iterator,
    text,
    on_empty_err,
):
    def print_err(text):
        print(f"\n{text}\n")

    # Begin searching
    count = 1
    choices = {}
    paginator = Paginator()

    # For next results
    choices['next'] = "next"

    # For previous results
    choices['previous'] = "previous"

    fetch = True
    while True:
        if fetch:
            items = []
            # 10 results displayed at the screen
            for _ in range(10):
                try:
                    items.append(next(iterator))
                except StopIteration:
                    break
            
            if items:
                paginator.add_page(*items)

                # Append choices for user input
                for item in items:
                    choices[str(count)] = item
                    count += 1
            else:
                try:
                    paginator.previous()
                except IndexError:
                    parser.error(on_empty_err)
                else:
                    print_err("[ERROR] There are no more results")

        def print_choices():
            # Build dynamic bars
            dynamic_bar = ""
            for _ in range(len(text)):
                dynamic_bar += "="
            
            print(dynamic_bar)
            print(text)
            print(dynamic_bar)

            paginator.print()
            
            print("")

            print("type \"next\" to show next results")
            print("type \"previous\" to show previous results")

        print_choices()

        # User input
        _next = False
        previous = False
        while True:
            choice = input_handle("=> ")
            try:
                item = choices[choice]
            except KeyError:
                print_err('[ERROR] Invalid choice, try again')
                print_choices()
                continue
            else:
                if item == "next":
                    _next = True
                elif item == "previous":
                    try:
                        paginator.previous()
                    except IndexError:
                        print_err('[ERROR] Choices are out of range, try again')
                        print_choices()
                        continue

                    previous = True
                break
        
        if _next:
            paginator.next()
            fetch = True
            continue
        elif previous:
            fetch = False
            continue
        else:
            break
    
    return item

def validate(parser, args):
    urls = args.URL

    if not args.search and not args.fetch_library:
        try:
            args.URL = validate_url(urls)
        except argparse.ArgumentTypeError as e:
            parser.error(str(e))
        return

    kwargs = {
        'parser': parser
    }

    if args.search:
        iterator = search(urls, args.unsafe)
        text = f"Search results for \"{urls}\""
        on_empty_err = f"Search results \"{urls}\" are empty"
    elif args.fetch_library:
        result = urls.split(':')
        
        # Try to get filter status
        try:
            status = result[1]
        except IndexError:
            status = None

        try:
            iterator = get_manga_from_user_library(status, args.unsafe)
        except MangaDexException as e:
            parser.error(str(e))
        
        user = Net.requests.user
        text = f"Manga library from user \"{user.name}\""
        on_empty_err = f"User \"{user.name}\" has no saved mangas"

    kwargs.update({
        'iterator': iterator,
        'text': text,
        'on_empty_err': on_empty_err
    })

    result = _create_prompt_choices(**kwargs)

    args.URL = validate_url(result.id)

def build_url(parser, args):
    validate(parser, args)

    if args.type:
        urls = []
        for parsed_url, orig_url in args.URL:
            url = build_URL_from_type(args.type, parsed_url)
            urls.append(url)
        args.URL = urls
    else:
        urls = []
        for parsed_url, orig_url in args.URL:
            url = smart_select_url(orig_url)
            urls.append(url)
        args.URL = urls