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

from enum import Enum

# Adapted from https://github.com/tachiyomiorg/tachiyomi-extensions/blob/master/src/all/mangadex/src/eu/kanade/tachiyomi/extension/all/mangadex/MangaDexFactory.kt
class Language(Enum):
    """List of MangaDex languages"""

    # The reason why in the end of each variables here
    # has "#:", because to showed up in sphinx documentation.
    English = 'en' #:
    Japanese = 'ja' #:
    Polish = 'pl' #:
    SerboCroatian = 'sh' #:
    Dutch = 'nl' #:
    Italian = 'it' #:
    Russian = 'ru' #:
    German = 'de' #:
    Hungarian = 'hu' #:
    French = 'fr' #:
    Finnish = 'fi' #:
    Vietnamese = 'vi' #:
    Greek = 'el' #:
    Bulgarian = 'bg' #:
    SpanishSpain = 'es' #:
    PortugueseBrazil = 'pt-br' #:
    PortuguesePortugal = 'pt' #:
    Swedish = 'sv' #:
    Arabic = 'ar' #:
    Danish = 'da' #:
    ChineseSimplified = 'zh' #:
    Bengali = 'bn' #:
    Romanian = 'ro' #:
    Czech = 'cs' #:
    Mongolian = 'mn' #:
    Turkish = 'tr' #:
    Indonesian = 'id' #:
    Korean = 'ko' #:
    SpanishLTAM = 'es-la' #:
    Persian = 'fa' #:
    Malay = 'ms' #:
    Thai = 'th' #:
    Catalan = 'ca' #:
    Filipino = 'tl' #:
    ChineseTraditional = 'zh-hk' #:
    Ukrainian = 'uk' #:
    Burmese = 'my' #:
    Lithuanian = 'lt' #:
    Hebrew = 'he' #:
    Hindi = 'hi' #:
    Norwegian = 'no' #:
    Nepali = 'ne' #:
    Kazakh = 'kk' #:
    Tamil = 'ta' #:
    Azerbaijani = 'az' #:
    Slovak = 'sk' #:

    # Other language
    Other = None #:

    # While all languages above is valid languages,
    # this one is not actually a language
    # it's just alias for all languages
    All = "all"

class RomanizedLanguage(Enum):
    RomanizedJapanese = 'ja-ro'
    RomanizedKorean = 'ko-ro'
    RomanizedChinese = 'zh-ro'

def get_language(lang):
    try:
        return Language[lang]
    except KeyError:
        pass
    return Language(lang)

def get_details_language(lang):
    # Retrieve base languages first
    try:
        return get_language(lang)
    except ValueError:
        pass

    # Retrieve romanized language
    try:
        return RomanizedLanguage[lang]
    except KeyError:
        pass
    return RomanizedLanguage(lang)