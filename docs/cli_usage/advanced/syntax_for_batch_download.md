# Special syntax for batch download

To avoid conflict filenames with reserved names (such as: `list`, `library`, `followed-list`) in `URL` argument, 
you can use special syntax for batch download

For example:

```shell
mangadex-dl "file:/home/manga/urls.txt"

mangadex-dl "file:list"
```

For more information, see {doc}`../../cli_ref/file_command`
