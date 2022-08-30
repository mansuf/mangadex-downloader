# What is this ?

Syntaxes for `--range` option. It's just a draft, these can be changed anytime in the future.

## Current solution

Syntax

```
volume[chapter[pages]]
```

### Formatted ver

```
1[
    2-5[
        1,
        2,
        3,
        4,
        5
    ], 
    2, 
    3, 
    4
]
```

### Non-formatted ver

```
1[2-5[1,2,3,4,5],2,3,4]
```

## JSON-based solution

Syntax

```json
{"volume": {"chapters": [pages]}}
```

### Formatted ver

```json
{
    "1": {
        "2-5": [
            "1",
            "2",
        ]
    }
}
```

### Non-formatted ver

```json
{"1": {"2-5": [1,2]}}
```

## Another solution

Syntax

```
{volume}:{chapter}:{pages}
```

```
1:2-5:1,2,3,4,5
```