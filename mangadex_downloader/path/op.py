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
