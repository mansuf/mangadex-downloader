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

# The rest of this codes is undocumented.
# Because there is too much to write
# especially with _parse_ptrn() and RangeChecker
# FIXME: give this codes a documentation

import re

from .errors import MangaDexException

__all__ = (
    'compile', 'purge_cache'
)

class InvalidPattern(MangaDexException):
    pass

def _err_invalid_ptrn(text, err_ptrn, msg):
    copy_text = str(text)
    # Append remaining pattern
    ptrn = ""
    for c in copy_text:
        if c == ",":
            break
        ptrn += c
    err_msg = f"Invalid pattern \"{err_ptrn + ptrn}\", "
    err_msg += msg
    raise InvalidPattern(err_msg)

def _parse_ptrn(_text):
    open_square_bracket = False
    close_square_bracket = False
    ptrn = ""
    text = ""
    base_char = None
    list_ptrn = []
    pages = []

    def reset_state():
        nonlocal open_square_bracket
        nonlocal close_square_bracket
        nonlocal ptrn
        nonlocal base_char
        nonlocal pages

        open_square_bracket = False
        close_square_bracket = False
        ptrn = ""
        base_char = None
        pages = []

    def reset_ptrn():
        nonlocal ptrn

        ptrn = ""

    def modify_text(char):
        nonlocal text

        text = text[len(char):]

    def append_ptrn(chap, pages, char=None):
        nonlocal list_ptrn

        list_ptrn.append((chap, pages))
        if char is not None:
            modify_text(char)
        reset_state()

    def check_next(text, char):
        return char == ","

    # Removing spaces in pattern
    for char in _text:
        if char == " ":
            continue
        
        text += char

    while True:
        if not text:

            if pages:

                if ptrn:
                    pages.append(ptrn)
                    reset_ptrn()

                append_ptrn(base_char, pages, None)
            elif (ptrn or base_char):
                append_ptrn(base_char + ptrn, [])

            break

        # Text is reached end of characters
        elif len(text) == 1 and text == ",":
            break

        for char in text:
            if not open_square_bracket and not close_square_bracket:

                if base_char is None:

                    if char == '[':
                        _err_invalid_ptrn(
                            text,
                            ptrn,
                            "There is no characters before square bracket"
                        )

                    if check_next(text, char):
                        continue

                    base_char = char
                    modify_text(char)
                    continue

                elif base_char:
                    if check_next(text, char):

                        ptrn = base_char + ptrn

                        if char != ',':
                            ptrn += char

                        append_ptrn(ptrn, [], char)

                    elif char == "[":
                        open_square_bracket = True
                        modify_text(char)
                        continue

                    else:
                        ptrn += char
                        modify_text(char)
                        continue

            if open_square_bracket and not close_square_bracket:
                
                # Duplicate opening square bracket
                if char == '[':
                    _err_invalid_ptrn(
                        text,
                        ptrn,
                        "Found duplicate opening square bracket"
                    )

                elif char == ']':
                    close_square_bracket = True
                    modify_text(char)
                    continue

                else:
                    if check_next(text, char):
                        pages.append(ptrn)
                        reset_ptrn()
                        modify_text(char)
                        continue

                    else:
                        ptrn += char
                        modify_text(char)
                        continue
            
            if open_square_bracket and close_square_bracket:

                if ptrn:
                    pages.append(ptrn)
                    reset_ptrn()

                append_ptrn(base_char, pages, char)
                continue

    return list_ptrn

class _Checker:
    ignored_chapters = []
    ignored_pages = {}

    def __init__(self, ptrn):
        self.ptrn = ptrn.lower()

    @classmethod
    def ignore_chapter(cls, num):
        if num.startswith('!'):
            num = num[1:] # Remove "!"

        cls.ignored_chapters.append(num)
    
    @classmethod
    def ignore_page(cls, chap, num):
        if num.startswith('!'):
            num = num[1:] # Remove "!"

        try:
            pages = cls.ignored_pages[chap]
        except KeyError:
            cls.ignored_pages[chap] = [num]
        else:
            pages.append(num)

    def _get_keyword(self, chap):
        keyword = ""
        if chap.oneshot:
            keyword = "oneshot"
        else:
            keyword = chap.chapter.lower() if chap.chapter is not None else ""
        
        return keyword

    def check(self, num):
        raise NotImplementedError

    def check_page(self, chap, num):
        num = str(num)
        try:
            ignored = num in self.ignored_pages[chap]
        except KeyError:
            ignored = False

        if ignored:
            return False

        return self.check(num)

    def check_chapter(self, chap):
        ignored = self._get_keyword(chap) in self.ignored_chapters
        if ignored:
            return False

        # oneshot checking
        if chap.oneshot and self.ptrn == 'oneshot':
            return True

        return self.check(chap.chapter)

class _RangeStartFrom(_Checker):
    def __init__(self, ptrn):
        super().__init__(ptrn)

        start, end = ptrn.split('-')
        self.start = float(start)

    def check(self, num):
        if num is None:
            # We can't do anything if num is "null"
            return True

        try:
            return float(num) >= self.start
        except ValueError:
            # Usually the chapter is non-floating numbers like "EXTRA"
            # Just return True
            return True

class _RangeEndFrom(_Checker):
    def __init__(self, ptrn):
        super().__init__(ptrn)
        
        start, end = ptrn.split('-')
        self.end = float(end)
    
    def check(self, num):
        if num is None:
            # We can't do anything if num is "null"
            return True

        try:
            return float(num) <= self.end
        except ValueError:
            # Usually the chapter is non-floating numbers like "EXTRA"
            # Just return True
            return True

class _RangeStarttoEnd(_Checker):
    def __init__(self, ptrn):
        super().__init__(ptrn)

        start, end = ptrn.split('-')
        self.start = float(start)
        self.end = float(end)

    def check(self, num):
        if num is None:
            # We can't do anything if num is "null"
            return True
        
        try:
            num = float(num)
        except ValueError:
            # Usually the chapter is non-floating numbers like "EXTRA"
            # Just return True
            return True

        if not (num >= self.start):
            return False
        
        if not (num <= self.end):
            return False
        
        return True

class _Check(_Checker):
    def __init__(self, ptrn):
        super().__init__(ptrn)
    
    def check(self, num):
        return num.lower() == self.ptrn

re_numbers = r''

# Start to end
re_numbers += r'(?P<starttoend>.{1,}-.{1,})|'

# End from
re_numbers += r'(?P<endfrom>.{0,}-.{1,})|'

# Start from
re_numbers += r'(?P<startfrom>.{1,}-.{0,})|'

# Ignored number
re_numbers += r'(?P<ignorednum>!.{1,})|'

# Check specified number
re_numbers += r'(?P<checknum>.{1,})'

checkers = {
    'starttoend': _RangeStarttoEnd,
    'startfrom': _RangeStartFrom,
    'endfrom': _RangeEndFrom,
    'checknum': _Check,
}

class _Pattern:
    range_checkers = [i for i in checkers.values() if i != _Check]

    def __init__(self, string):
        self.ignored = string.startswith('!')

        if self.ignored:
            string = string[1:] # Remove "!"

        self.string = string

    def get_type(self):
        match = re.match(re_numbers, self.string)
        for _type, val in match.groupdict().items():
            if val is not None:
                break

        return _type
    
    def get_cls(self):
        chk = checkers[self.get_type()]

        for cls in self.range_checkers:
            if chk == cls:
                # Non-numbers are not allowed to use range pattern
                start, end = self.string.split('-')

                is_number = True

                if start:
                    try:
                        float(start)
                    except ValueError:
                        is_number = False

                if end:
                    try:
                        float(end)
                    except ValueError:
                        is_number = False

                if not is_number:
                    raise InvalidPattern(
                        f"Invalid pattern \"{self.string}\", " \
                         "Non-numbers are not allowed to use range pattern"
                    )
                elif self.ignored:
                    raise InvalidPattern(
                        f"Invalid pattern \"{self.string}\", " \
                        "ignore (!) symbol are not supported when used with range pattern"
                    )

        return chk

class RangeChecker:
    """A class to compile range pattern and check if chapters is downloadable from range pattern
    
    client should not create this, instead use :meth:`compile()`
    """
    def __init__(self, ptrn):
        self.patterns = _parse_ptrn(ptrn)
        self.checkers = []
        self._parse()

    def _create_checker(self, num):
        ptrn = _Pattern(num)
        cls = ptrn.get_cls()
        return ptrn, cls(num)
    
    def _create_checker_chapter(self, num):
        ptrn, checker = self._create_checker(num)
        if ptrn.ignored:
            _Checker.ignore_chapter(num)
        
        return checker

    def _create_checker_page(self, chap, num):
        ptrn, checker = self._create_checker(num)
        if ptrn.ignored:
            _Checker.ignore_page(chap, num)
        
        return checker

    def _parse(self):
        for chapter, pages in self.patterns:
            page_checkers = []
            chapter_checker = self._create_checker_chapter(chapter)

            for page in pages:
                page_checker = self._create_checker_page(chapter, page)
                page_checkers.append(page_checker)
            
            self.checkers.append((chapter_checker, page_checkers))
        
    def check_page(self, chapter, num):
        found = False
        for chap, pages in self.checkers:

            if chap.ptrn == chapter.chapter:

                if not pages:
                    # If inside chapter pattern there is no pages
                    # We must mark it as found = True
                    # to avoid all pages getting ignored

                    found = True
                    break

                for page in pages:

                    found = page.check_page(chapter.chapter, num)
                    if found:
                        break

        return found

    def check_chapter(self, chapter):
        found = False

        for chap, _ in self.checkers:
            found = chap.check_chapter(chapter)
            if found:
                break
        
        return found

_caches = {}

def compile(pattern: str) -> RangeChecker:
    """Compile a range pattern into :class:`RangeChecker`"""
    # Check if cached
    cls = _caches.get(pattern)
    if cls:
        return cls

    cls = RangeChecker(pattern)
    
    # Store it to cache
    _caches[pattern] = cls

    return cls

def purge_cache():
    """Purge :class:`RangeChecker` cache"""
    _caches.clear()

