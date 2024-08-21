# Blacklist a group or user

Sometimes you don't like the chapter that this user or group upload it. 
You can use this feature to prevent the chapter being downloaded.

## Group

```shell
# For Windows
set MANGADEXDL_GROUP_BLACKLIST=4197198b-c99b-41ae-ad21-8e6ecc10aa49, 0047632b-1390-493d-ad7c-ac6bb9288f05

# For Linux / Mac OS
export MANGADEXDL_GROUP_BLACKLIST=4197198b-c99b-41ae-ad21-8e6ecc10aa49, 0047632b-1390-493d-ad7c-ac6bb9288f05
```

## User

```shell
# For Windows
set MANGADEXDL_USER_BLACKLIST=1c4d814e-b1c1-4b75-8a69-f181bb4e57a9, f8cc4f8a-e596-4618-ab05-ef6572980bbf

# For Linux / Mac OS
export MANGADEXDL_USER_BLACKLIST=1c4d814e-b1c1-4b75-8a69-f181bb4e57a9, f8cc4f8a-e596-4618-ab05-ef6572980bbf
```

For more information, see {doc}`../../cli_ref/env_vars`
