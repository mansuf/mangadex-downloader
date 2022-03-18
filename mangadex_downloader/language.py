from enum import Enum

# Adapted from https://github.com/tachiyomiorg/tachiyomi-extensions/blob/master/src/all/mangadex/src/eu/kanade/tachiyomi/extension/all/mangadex/MangaDexFactory.kt#L54-L96
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