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

import sys

import requests
from .utils import (
    Paginator, 
    dynamic_bars, 
    IteratorEmpty, 
    get_key_value, 
    split_comma_separated
)
from ..iterator import (
    IteratorManga,
    IteratorMangaFromList,
    IteratorSeasonalManga,
    IteratorUserLibraryFollowsList,
    IteratorUserLibraryList,
    IteratorUserLibraryManga,
    IteratorUserList,
    iter_random_manga,
    ForumThreadMangaDexURLIterator
)
from ..forums import (
    get_thread_title_owner_and_post_owner,
    get_post_id_forum_thread
)
from .. import __repository__
from ..utils import input_handle, validate_url, get_cover_art_url
from ..errors import InvalidURL, MangaDexException, PillowNotInstalled
from ..network import Net
from ..manga import Manga
from ..chapter import Chapter
from ..mdlist import MangaDexList
from ..group import Group

def preview_chapter(chapter: Chapter):
    try:
        from PIL import Image
    except ImportError:
        raise PillowNotInstalled("Pillow is not installed") from None

    # we're just gonna use chapter info (cover)
    url = f"https://og.mangadex.org/og-image/chapter/{chapter.id}"
    r = Net.mangadex.get(url, stream=True)
    im = Image.open(r.raw)

    print("\nCLOSE THE IMAGE PREVIEW TO CONTINUE\n")

    im.show(str(chapter))
    im.close()

    pass

def preview_cover_manga(manga):
    try:
        from PIL import Image
    except ImportError:
        raise PillowNotInstalled("Pillow is not installed") from None

    cover_art_url = get_cover_art_url(manga, manga.cover, "original")
    r = Net.mangadex.get(cover_art_url, stream=True)
    im = Image.open(r.raw)

    print("\nCLOSE THE IMAGE PREVIEW TO CONTINUE\n")

    im.show(manga.title)
    im.close()

def preview_list(mdlist):
    text_init = f'List of mangas from MangaDex list \"{mdlist.name}\"'

    print('\n')
    print(text_init)
    print(dynamic_bars(text_init))
    for manga in mdlist.iter_manga():
        print(manga.title)
    print('\n\n')

class BaseCommand:
    """A base class that will handle command prompt"""
    def __init__(self, parser, args, iterator, text, limit=10):
        self.args_parser = parser
        self.args = args
        self.text = text
        self.paginator = Paginator(iterator, limit)
        self._text_choices = ""

    def _error(self, message, exit=False):
        """Function to print error, yes"""
        msg = f'\nError: {message}\n'
        if exit:
            self.args_parser.error(message)
        else:
            print(msg)

    def _insert_choices(self, choices, action='next'):
        text = ""
        func = getattr(self.paginator, action)

        for pos, item in func():
            choices[str(pos)] = item
            text += f"({pos}). {item}\n" 

        self._text_choices = text

    def _print_choices(self):
        header = dynamic_bars(self.text) + "\n"

        final_text = ""
        # Title with bars header
        final_text += header
        final_text += self.text + "\n"
        final_text += header

        # Choices
        final_text += self._text_choices

        # Empty line for separator
        final_text += "\n"

        # Prompt instruction
        final_text += 'type "next" to show next results\n'
        final_text += 'type "previous" to show previous results'
        if self.preview():
            final_text += '\ntype "preview NUMBER" to show more details about selected result. ' \
                          'For example: "preview 2"'
        
        print(final_text)

    def preview(self):
        """Check if this command support preview.
        
        Must return ``True`` or ``False``.
        """
        return False

    def on_empty_error(self):
        """This function will be called if :attr:`BaseCommand.iterator` 
        returns nothing on first prompt.
        """
        pass

    def on_preview(self, item):
        """This function is called when command ``preview`` is selected.
        
        :func:`BaseCommand.preview()` must return ``True`` in order to get this called.
        """
        pass

    def _return_from(self, pos):
        choices = {}

        try:
            self._insert_choices(choices)
        except IteratorEmpty:
            self.on_empty_error()
            return None

        while True:

            try:
                result = choices[pos]
            except KeyError:
                result = None
            
            if result is not None:
                yield result
                break
            elif pos == "*":
                for item in choices.values():
                    yield item

            try:
                self._insert_choices(choices)
            except IteratorEmpty:
                self._error("There are no more results", exit=True)
            except IndexError:
                self._error("Choices are out of range, try again")

    def prompt(self, input_pos=None):
        """Begin ask question to user"""
        choices = {}

        if input_pos:
            return self._return_from(input_pos)

        # Begin inserting choices for question
        try:
            self._insert_choices(choices)
        except IteratorEmpty:
            self.on_empty_error()
            return

        answer = None
        while True:
            if answer is not None:
                if answer.startswith('preview') and self.preview():
                    answer_item = answer.split('preview', maxsplit=1)[1].strip()
                    try:
                        item = choices[answer_item]
                    except KeyError:
                        self._error("Invalid choice, try again")
                    else:
                        self.on_preview(item)

                    answer = None
                    continue

                elif answer.startswith("next"):
                    action = "next"
                elif answer.startswith("previous"):
                    action = "previous"
                else:
                    try:
                        item = choices[answer]
                    except KeyError:
                        self._error("Invalid choice, try again")
                        answer = None
                    else:
                        return item
                
                if answer is not None:
                    try:
                        self._insert_choices(choices, action)
                    except IteratorEmpty:
                        self._error("There are no more results")
                    except IndexError:
                        self._error("Choices are out of range, try again")
        
            self._print_choices()
            answer = input_handle("=> ")

class MangaDexCommand(BaseCommand):
    """Command specialized for MangaDex"""
    def prompt(self, input_pos=None):
        answer = super().prompt(input_pos=input_pos)

        def yield_ids():
            for item in answer:
                item_id = getattr(item, "id", None)
                if item_id:
                    yield item_id
                else:
                    yield item

        # "input_pos" argument from prompt() is used
        if input_pos:
            return yield_ids()
        else:
            return [answer.id]

class MangaCommand(MangaDexCommand):
    """Command specialized for manga related"""
    def preview(self):
        return True

    def on_preview(self, item):
        preview_cover_manga(item)

class MDListCommand(MangaDexCommand):
    """Command specialized for MangaDex list related"""
    def preview(self):
        return True

    def on_preview(self, item):
        preview_list(item)

class MangaLibraryCommand(MangaCommand):
    """A command that will prompt user to select which manga want to download from user library"""

    def __init__(self, parser, args, input_text):
        _, status = get_key_value(input_text, sep=':')

        if not status:
            # To prevent error "invalid value"
            status = None
        elif status == "help":
            text = "List of statuses filter for user library manga"

            bars = dynamic_bars(text)

            print(f"{bars}\n{text}\n{bars}")
            for item in IteratorUserLibraryManga.statuses:
                print(item)
            parser.exit(0)

        user = Net.mangadex.user

        super().__init__(
            parser,
            args,
            IteratorUserLibraryManga(status),
            f'List of manga from user library "{user.name}"'
        )

        self.user = user

    def on_empty_error(self):
        self.args_parser.error(f'User "{self.user.name}"')

class ListLibraryCommand(MDListCommand):
    """A command that will prompt user to select which list want to download from user library"""
    def __init__(self, parser, args, input_text):
        _, user = get_key_value(input_text, sep=':')

        user_id = None
        if user:
            try:
                user_id = validate_url(user)
            except InvalidURL as e:
                parser.error(f'"{user}" is not a valid user')
        
        if user:
            iterator = IteratorUserList(user_id)
        else:
            iterator = IteratorUserLibraryList()
        
        try:
            user = iterator.user
        except AttributeError:
            # Logged in user
            user = Net.mangadex.user

        super().__init__(
            parser,
            args,
            iterator,
            f'List of saved MDList from user "{user.name}"'
        )

        self.user = user
    
    def on_empty_error(self):
        self.args_parser.error(f'User "{self.user.name} has no saved lists"')

class FollowedListLibraryCommand(MDListCommand):
    """A command that will prompt user to select which list want to download from followed lists user """

    def __init__(self, parser, args, input_text):
        iterator = IteratorUserLibraryFollowsList()

        user = Net.mangadex.user

        super().__init__(
            parser,
            args,
            iterator,
            f'List of followed MDlist from user "{user.name}"'
        )

        self.user = user
    
    def on_empty_error(self):
        self.args_parser.error(f'User "{self.user.name}" has no followed lists')

class FilterEnabled:
    @classmethod
    def parse_filter(cls, args):
        # Parse filters
        orders = {}
        filter_kwargs = {}
        filters = args.filter or []
        for f in filters:
            key, value  = get_key_value(f)
            try:
                value_filter_kwargs = filter_kwargs[key]
            except KeyError:
                filter_kwargs[key] = split_comma_separated(value)
            else:
                # Found duplicate filter with different value
                if isinstance(value_filter_kwargs, str):
                    new_values = [value_filter_kwargs]
                else:
                    new_values = value_filter_kwargs

                values = split_comma_separated(value, single_value_to_list=True)
                new_values.extend(values)

                filter_kwargs[key] = new_values

        # We cannot put "order[key]" into function parameters
        # that would cause syntax error
        for key in filter_kwargs.keys():
            if 'order' in key:
                orders[key] = filter_kwargs[key]

        # Remove "order[key]" from filter_kwargs
        # to avoid syntax error
        for key in orders.keys():
            filter_kwargs.pop(key)

        # This much safer
        if orders:
            filter_kwargs['order'] = orders

        return filter_kwargs

class SearchMangaCommand(MangaCommand, FilterEnabled):
    """A command that will prompt user to select which manga to download (from search)"""
    def __init__(self, parser, args, input_text):
        filter_kwargs = self.parse_filter(args)

        iterator = IteratorManga(input_text, **filter_kwargs)
        super().__init__(
            parser,
            args,
            iterator,
            f'Manga search results for "{input_text}"'
        )
        
        self.input_text = input_text
    
    def on_empty_error(self):
        self.args_parser.error(f'Manga search results for "{self.input_text}" are empty')

class GroupMangaCommand(MangaCommand):
    """A command that will prompt user to select which manga to download (from scanlator group)"""
    def __init__(self, parser, args, input_text):
        # Getting group id
        _, group_id = get_key_value(input_text, sep=':')
        if not group_id:
            parser.error("group id or url are required")
        
        group_id = validate_url(group_id)
        group = Group(group_id)

        iterator = IteratorManga(None, group=group.id)
        text = f'List of manga from group "{group.name}"'

        super().__init__(
            parser,
            args,
            iterator,
            text
        )
        
        self.group = group

    def on_empty_error(self):
        self.args_parser.error(f'Group "{self.group.name}" has no uploaded mangas')

class RandomMangaCommand(MangaCommand, FilterEnabled):
    def __init__(self, parser, args, input_text):
        _, value = get_key_value(input_text, sep=':')

        if value:
            raise MangaDexException(
                "Syntax 'random:<content_rating>' are no longer supported, " \
                "use --filter or -ft instead."
            )

        filters = self.parse_filter(args)

        iterator = iter_random_manga(**filters)
        text = f'Found random manga'
        super().__init__(
            parser,
            args,
            iterator,
            text,
            limit=5
        )
    
    def on_empty_error(self):
        # This should never happened
        self.args_parser.error('Unknown error when fetching random manga')

class SeasonalMangaCommand(MangaCommand):
    def __init__(self, parser, args, input_text):
        # Get season
        _, season = get_key_value(input_text, sep=':')

        season = season.lower().strip()

        if season == "list":
            self._print_help()
        elif not season:
            # Current season
            r = Net.requests.get(f'https://raw.githubusercontent.com/{__repository__}/main/seasonal_manga_now.txt')
            try:
                r.raise_for_status()
            except requests.HTTPError as e:
                raise MangaDexException(f"failed to get current seasonal manga, reason: {e}")
            
            season_list_id = validate_url(r.text)
            iterator = IteratorMangaFromList(season_list_id)
            season = iterator.name
        else:
            season = f'Seasonal: {season.capitalize()}'
            iterator = IteratorSeasonalManga(season)

        text = f"List of manga from {season}"
        super().__init__(
            parser,
            args,
            iterator,
            text
        )

    def _print_help(self):
        header = "Available seasons"

        print(header)
        print(dynamic_bars(header), end='\n\n')

        for season in IteratorSeasonalManga._get_seasons():
            print(season)
        
        sys.exit(0)

    def on_empty_error(self):
        # This should never happened
        self.args_parser.error('Unknown error when fetching seasonal manga')

class ForumThreadCommand(MangaDexCommand):
    def preview(self):
        return True

    def on_preview(self, item):
        if isinstance(item, Manga):
            preview_cover_manga(item)
        elif isinstance(item, Chapter):
            preview_chapter(item)
        elif isinstance(item, MangaDexList):
            preview_list(item)

    def __init__(self, parser, args, input_text):
        iterator = ForumThreadMangaDexURLIterator(input_text, True)

        post_id = get_post_id_forum_thread(input_text)
        result = get_thread_title_owner_and_post_owner(thread_url=input_text, post_id=post_id)
        thread_title, thread_owner, post_owner = result

        text = f"List of URLs from thread '{thread_title}' by '{thread_owner}'"

        if post_owner:
            text += f" post by '{post_owner}'"

        super().__init__(
            parser,
            args,
            iterator,
            text,
            limit=5
        )

    def _return_from(self, pos):
        # We don't want to fetch the entire URLs returned from forum thread
        # when --input-pos is used
        self.paginator.iterator.fetch = False

        return super()._return_from(pos)
    
    def on_empty_error(self):
        self.args_parser.error("No MangaDex urls found in the forum thread")

registered_commands = {
    "search": SearchMangaCommand,
    "fetch_library_manga": MangaLibraryCommand,
    "fetch_library_list": ListLibraryCommand,
    "fetch_library_follows_list": FollowedListLibraryCommand,
    "random": RandomMangaCommand,
    "fetch_group": GroupMangaCommand,
    "seasonal": SeasonalMangaCommand,
    "thread": ForumThreadCommand
}