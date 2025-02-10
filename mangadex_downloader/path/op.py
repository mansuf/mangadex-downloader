from .placeholders import Placeholder, create_placeholders_kwargs


def get_filename(manga, obj, file_ext, format="chapter"):
    from ..config import config

    # Append `file_ext` to placeholders
    attributes = Placeholder.get_allowed_attributes()

    cli_option = f"--filename-{format}"

    fmt_kwargs = create_placeholders_kwargs(manga, attributes, cli_option=cli_option)
    fmt_kwargs["file_ext"] = Placeholder(
        obj=file_ext,
        name="file_ext",
        allowed_attributes=attributes,
        cli_option=cli_option,
    )

    p = Placeholder(
        obj=obj,
        name=format.capitalize(),
        allowed_attributes=attributes,
        cli_option=cli_option,
    )

    if format == "volume":
        # to bypass error "you must use attribute in placeholder bla bla bla"
        p.has_attr = False

    # Special treatment for single format
    # Because `chapters` is the only placeholders that can be used
    # for single format
    if format == "single":
        fmt_kwargs["chapters"] = p
    else:
        fmt_kwargs[format] = p

    return getattr(config, f"filename_{format}").format(**fmt_kwargs)


def get_path(manga):
    from ..config import config

    attributes = Placeholder.get_allowed_attributes(
        file_ext=False, chapter=False, volume=False
    )
    fmt_kwargs = create_placeholders_kwargs(
        manga, attributes=attributes, cli_option="--path"
    )

    return config.path.format(**fmt_kwargs)


def get_manga_info_filepath(manga):
    from ..config import config

    attributes = Placeholder.get_allowed_attributes(
        file_ext=False, chapter=False, volume=False
    )
    fmt_kwargs = create_placeholders_kwargs(
        manga, attributes=attributes, cli_option="--manga-info-filepath"
    )

    # Workaround for "mihon" manga info format
    # If we do not do this, the file extension will end up as ".mihon" instead of ".json"
    if config.manga_info_format == "mihon":
        manga_info_format = "json"
    else:
        manga_info_format = config.manga_info_format

    # Because this is modified placeholders
    # in order for get_manga_info_filepath() to work
    # We need to include some attributes before creating placeholders
    # to prevent crashing (KeyError) when initialize Placeholder class
    attributes["manga_info_format"] = None
    attributes["download_path"] = None

    fmt_kwargs["manga_info_format"] = Placeholder(
        obj=manga_info_format,
        name="manga_info_format",
        allowed_attributes=attributes,
    )
    fmt_kwargs["download_path"] = Placeholder(
        obj=get_path(manga), name="download_path", allowed_attributes=attributes
    )

    return config.manga_info_filepath.format(**fmt_kwargs)
