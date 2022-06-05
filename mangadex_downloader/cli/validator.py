import argparse
import os
import sys

from .utils import Paginator, dynamic_bars
from .url import build_URL_from_type, smart_select_url
from ..network import Net
from ..main import get_followed_list_from_user_library, get_list_from_user, get_list_from_user_library, search, get_manga_from_user_library
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
    on_preview
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

    # To see more details about selected result
    if on_preview:
        choices['preview'] = "preview"

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

            if on_preview:
                print(
                    "type \"preview NUMBER\" to show more details about selected result. " \
                    "For example: \"preview 2\""
                )

        print_choices()

        # User input
        _next = False
        previous = False
        preview = False
        while True:
            choice = input_handle("=> ")

            # Parsing on_view
            if choice.startswith('preview'):
                choice = choice.split('preview')[1].strip()
                preview = True

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
        elif preview:
            fetch = False
            on_preview(item)
            continue
        else:
            break
    
    return item

def preview_list(args, mdlist):
    cache = []
    for manga in mdlist.iter_manga(args.unsafe):
        cache.append(manga)

    len_manga_titles = []
    # Grab the longest title to determine length bar
    for manga in cache:
        len_manga_titles.append(len(manga.title))
    
    # List is empty
    if not len_manga_titles:
        length_bar = 0
    else:
        length_bar = max(len_manga_titles)

    print('\n')
    print(f'List of mangas from MangaDex list \"{mdlist.name}\"')
    print(dynamic_bars(length_bar))
    for manga in cache:
        print(manga.title)
    print(f'{dynamic_bars(length_bar)}\n\n')

def validate(parser, args):
    urls = args.URL

    if (
        not args.search and 
        not args.fetch_library_manga and
        not args.fetch_library_list and
        not args.fetch_library_follows_list
    ):
        # Parsing file path
        if args.file:
            result = urls.split(':')
            file = result[1:]
            file_path = ""
            err_file = False

            try:
                file_path += file.pop(0)
            except IndexError:
                err_file = True
            
            if not file_path:
                err_file = True

            if err_file:
                parser.error("Syntax error: file path argument is empty")

            # Because ":" was removed during .split()
            # add it again
            for f in file:
                file_path += ':' + f
            
            # Because this is specified syntax for batch downloading
            # If file doesn't exist, raise error
            if not os.path.exists(file_path):
                parser.error(f"File \"{file_path}\" is not exist")
        else:
            file_path = urls
        try:
            args.URL = validate_url(file_path)
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
        on_preview = None
    elif args.fetch_library_manga:
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
        on_preview = None
    elif args.fetch_library_list:
        # Try to get user (if available)
        user = "".join(urls.split(':')[1:])

        user_id = None
        if user:
            try:
                user_id = __validate(user)
            except InvalidURL as e:
                parser.error(f"\"{user}\" is not a valid user")

        try:
            if user:
                iterator = get_list_from_user(user_id)
            else:
                iterator = get_list_from_user_library()
        except MangaDexException as e:
            parser.error(str(e))

        user = iterator.user if Net.requests.user is None else Net.requests.user
        text = f"MangaDex List library from user \"{user.name}\""
        on_empty_err = f"User \"{user.name}\" has no saved lists"
        on_preview = lambda x: preview_list(args, x)
    elif args.fetch_library_follows_list:
        try:
            iterator = get_followed_list_from_user_library()
        except MangaDexException as e:
            parser.error(str(e))
        
        user = Net.requests.user
        text = f"MangaDex followed List from user \"{user.name}\""
        on_empty_err = f"User \"{user.name}\" has no followed lists"
        on_preview = lambda x: preview_list(args, x)

    kwargs.update({
        'iterator': iterator,
        'text': text,
        'on_empty_err': on_empty_err,
        'on_preview': on_preview
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