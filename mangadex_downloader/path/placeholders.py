from pathvalidate import sanitize_filename
from ..utils import comma_separated_text
from ..language import Language as L, get_language
from ..network import Net
from ..errors import InvalidPlaceholders


class Language:
    def __init__(self, lang: L):
        if isinstance(lang, str):
            lang = get_language(lang)

        self.simple = lang.value
        self.full = lang.name


def _get_volume(x):
    if x is None:
        return "No volume"

    return f"Vol. {x}"


def _get_or_minus_one(x):
    if not x:
        return "-1"

    return x


def _split_text(text):
    return comma_separated_text(text, no_bracket=True)


class Placeholder:
    def __init__(self, obj, name=None, allowed_attributes=None, cli_option=None):
        self.obj = obj
        self.has_attr = True
        self.cli_option = cli_option
        self.obj_name = name if name else obj.__class__.__name__

        if allowed_attributes is not None:
            attr = allowed_attributes
        else:
            attr = self.get_allowed_attributes()

        attr = attr[self.obj_name]

        if not isinstance(attr, dict):
            # It's not dict type
            # see `Format` in self.get_allowed_attributes()
            # var "attr" in this case is modifier function
            value = attr(obj) if attr is not None else obj

            setattr(self, self.obj_name, value)
            self.has_attr = False
            return

        if obj is None:
            # We can't do anything if origin object is null
            return

        # Copy "allowed" origin attributes to this class
        for attr, modifier in attr.items():
            value = getattr(obj, attr)

            if modifier:
                value = modifier(value)

            setattr(self, attr, value)

    def __str__(self):
        if self.has_attr:
            raise InvalidPlaceholders(
                "You must use attribute for placeholder "
                f"{self.obj_name!r} in {self.cli_option!r} option"
            )
        return self.obj.__str__()

    @classmethod
    def get_allowed_attributes(
        cls,
        manga=True,
        chapter=True,
        volume=True,
        single=True,
        user=True,
        language=True,
        format=True,
        file_ext=True,
    ):
        attr = {}

        if manga:
            attr["Manga"] = {
                # Allowed attribute and modifier (function)
                "title": sanitize_filename,
                "id": None,
                "alternative_titles": None,
                "description": sanitize_filename,
                "authors": _split_text,
                "artists": _split_text,
                "cover": None,
                "genres": _split_text,
                "status": None,
                "content_rating": None,
                "tags": lambda x: _split_text([i.name for i in x]),
            }

        if chapter:
            attr["Chapter"] = {
                "chapter": _get_or_minus_one,
                "volume": _get_or_minus_one,
                "title": sanitize_filename,
                "pages": None,
                "language": None,
                "name": None,
                "simple_name": None,
                "groups_name": sanitize_filename,
            }

        if user:
            attr["User"] = {"id": None, "name": None}

        if language:
            attr["Language"] = {"simple": None, "full": None}

        if format:
            attr["Format"] = None

        if file_ext:
            attr["file_ext"] = None

        if volume:
            attr["Volume"] = {"chapters": None}

        if single:
            attr["Single"] = {"first": None, "last": None}

        return attr


def create_placeholders_kwargs(manga, attributes=None, cli_option=None):
    from ..config import config

    return {
        "manga": Placeholder(
            obj=manga, allowed_attributes=attributes, cli_option=cli_option
        ),
        "user": Placeholder(
            obj=Net.mangadex.user,
            name="User",
            allowed_attributes=attributes,
            cli_option=cli_option,
        ),
        "language": Placeholder(
            obj=Language(manga.chapters.language),
            name="Language",
            allowed_attributes=attributes,
            cli_option=cli_option,
        ),
        "format": Placeholder(
            obj=config.save_as,
            name="Format",
            allowed_attributes=attributes,
            cli_option=cli_option,
        ),
    }
