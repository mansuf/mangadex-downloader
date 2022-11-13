# Environment variables

```{option} MANGADEXDL_CONFIG_ENABLED [1 or 0, true or false]
Set this `1` or `true` to enable config, `0` or `false` to disable config.
```

```{option} MANGADEXDL_CONFIG_PATH
A directory to store config and authentication cache.
```

```{option} MANGADEXDL_ZIP_COMPRESSION_TYPE
Set zip compression type for any `cbz` and `epub` formats, 
by default it setted to `stored`

Must be one of:

- stored
- deflated
- bzip2
- lzma

For more information, see https://docs.python.org/3/library/zipfile.html#zipfile.ZIP_STORED
```

````{option} MANGADEXDL_ZIP_COMPRESSION_LEVEL
Set zip compression level for any `cbz` and `epub` formats.

```{note}
Zip compression type `stored` or `lzma` has no effect
```

levels:

- deflated : 0-9
- bzip2    : 1-9

For more information about each levels zip compression, 
see https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile
````

````{option} MANGADEXDL_GROUP_BLACKLIST [VALUE1, VALUE2, ...]
Add groups to blacklist. 
This to prevent chapter being downloaded from blacklisted groups.

Value must be file path, uuid, MangaDex url containing uuid. 
Multiple values is supported (separated by comma)

**Example usage (from a file)**

```shell
# inside of blocked_groups.txt

https://mangadex.org/group/4197198b-c99b-41ae-ad21-8e6ecc10aa49/no-group-scanlation
https://mangadex.org/group/0047632b-1390-493d-ad7c-ac6bb9288f05/ateteenplus
https://mangadex.org/group/1715d32d-0bf0-46e2-b8ad-a64386523038/afterlife-scans
```

```
# For Windows
set MANGADEXDL_GROUP_BLACKLIST=blocked_groups.txt

# For Linux / Mac OS
export MANGADEXDL_GROUP_BLACKLIST=blocked_groups.txt
```

**Example usage (uuid)**

```shell
# For Windows
set MANGADEXDL_GROUP_BLACKLIST=4197198b-c99b-41ae-ad21-8e6ecc10aa49, 0047632b-1390-493d-ad7c-ac6bb9288f05

# For Linux / Mac OS
export MANGADEXDL_GROUP_BLACKLIST=4197198b-c99b-41ae-ad21-8e6ecc10aa49, 0047632b-1390-493d-ad7c-ac6bb9288f05
```
````

````{option} MANGADEXDL_USER_BLACKLIST [VALUE1, VALUE2, ...]
Add users to blacklist. 
This to prevent chapter being downloaded from blacklisted users.

```{note}
Group blacklisting takes priority over user blacklisting
```

Value must be file path, uuid, MangaDex url containing uuid. 
Multiple values is supported (separated by comma)

**Example usage (from a file)**

```shell
# inside of blocked_users.txt

https://mangadex.org/user/f8cc4f8a-e596-4618-ab05-ef6572980bbf/tristan9
https://mangadex.org/user/81304b72-005d-4e62-bea6-4cb65869f7da/bravedude8
```

```
# For Windows
set MANGADEXDL_USER_BLACKLIST=blocked_users.txt

# For Linux / Mac OS
export MANGADEXDL_USER_BLACKLIST=blocked_users.txt
```

**Example usage (uuid)**

```shell
# For Windows
set MANGADEXDL_USER_BLACKLIST=1c4d814e-b1c1-4b75-8a69-f181bb4e57a9, f8cc4f8a-e596-4618-ab05-ef6572980bbf

# For Linux / Mac OS
export MANGADEXDL_USER_BLACKLIST=1c4d814e-b1c1-4b75-8a69-f181bb4e57a9, f8cc4f8a-e596-4618-ab05-ef6572980bbf
```
````

````{option} MANGADEXDL_TAGS_BLACKLIST [VALUE1, VALUE2, ...]
Add tags to blacklist. 
This to prevent manga being downloaded if it's contain one or more blacklisted tags.

Value must be file path, keyword, uuid, MangaDex url containing uuid. 
Multiple values is supported (separated by comma)

**Example usage (from a file)**

```shell
# inside of blocked_tags.txt

boys' love
girls' love
https://mangadex.org/tag/b29d6a3d-1569-4e7a-8caf-7557bc92cd5d/gore
```

```
# For Windows
set MANGADEXDL_TAGS_BLACKLIST=blocked_tags.txt

# For Linux / Mac OS
export MANGADEXDL_TAGS_BLACKLIST=blocked_tags.txt
```

**Example usage (keyword)**

```shell
# For Windows
set MANGADEXDL_GROUP_BLACKLIST=gore, girls' love

# For Linux / Mac OS
export MANGADEXDL_GROUP_BLACKLIST=gore, girls' love
```

**Example usage (uuid)**

```shell
# For Windows
set MANGADEXDL_GROUP_BLACKLIST=b29d6a3d-1569-4e7a-8caf-7557bc92cd5d, a3c67850-4684-404e-9b7f-c69850ee5da6

# For Linux / Mac OS
export MANGADEXDL_GROUP_BLACKLIST=b29d6a3d-1569-4e7a-8caf-7557bc92cd5d, a3c67850-4684-404e-9b7f-c69850ee5da6
```
````