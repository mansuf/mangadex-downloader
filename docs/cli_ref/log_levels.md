# Logging levels

mangadex-downloader are using python logging from standard library, 
for more information you can read it here -> https://docs.python.org/3/library/logging.html#logging-levels

Logging levels are determined by numeric values. 
The table are showed below:

| Level | Numeric value |
| ----- | ------------- |
| CRITICAL | 50 |
| ERROR | 40 |
| WARNING | 30 |
| INFO | 20 |
| DEBUG | 10 |
| NOTSET | 0 |

Example formula for logging levels:

If you set logging level to WARNING (which numeric value is 30), 
all logs that has WARNING level and above (ERROR and CRITICAL) will be visible.

Same goes for INFO and DEBUG.

If you set logging level to INFO (which numeric value is 20), 
all logs that has INFO level and above (WARNING, ERROR, CRITICAL) will be visible.

```{note}
If you set logging level to `NOTSET`, all logs will be not visible at all.
```

## Syntax

Accessible from `--log-level` option

## Example usage

```sh
# DEBUG (verbose) output
mangadex-dl "Insert MangaDex URL here" --log-level "DEBUG"

# WARNING output
mangadex-dl "Insert MangaDex URL here" --log-level "WARNING"
```
