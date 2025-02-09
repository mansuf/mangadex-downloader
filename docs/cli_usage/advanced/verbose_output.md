# Enable verbose output / change logging level

Starting v2.10.0, you can enable verbose output from `--log-level` with value `DEBUG`.

```sh
mangadex-dl "insert MangaDex URL here" --log-level "DEBUG"
```

Change logging level to warning.

```{note}
This level will only show output if the levels are warning, error and critical

For more information, see {doc}`../../cli_ref/log_levels`
```

```sh
mangadex-dl "insert MangaDex URL here" --log-level "WARNING"
```
