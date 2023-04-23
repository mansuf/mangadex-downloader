# MIT License

# Copyright (c) 2022-present Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This module containing JSON operations 
# where the library use `json` or `orjson` (if available) streamlined
# without using different behaviour each libraries
# ex: dumped JSON (orjson) -> bytes
# ex: dumped JSON (json) -> str

import json
import chardet
from typing import Union

try:
    import orjson
except ImportError:
    ORJSON_OK = False
else:
    ORJSON_OK = True

__all__ = ("loads", "dumps", "JSONDecodeError", "JSONEncodeError")

# List of errors
if ORJSON_OK:
    JSONDecodeError = orjson.JSONDecodeError
    JSONEncodeError = orjson.JSONEncodeError
else:
    JSONDecodeError = json.JSONDecodeError
    JSONEncodeError = TypeError
    

def _get_encoding(content):
    data = bytearray(content)
    detector = chardet.UniversalDetector()
    while data:
        feed = data[:4096]
        detector.feed(feed)
        if detector.done:
            break

        del data[:4096]

    if not detector.done:
        detector.close()

    return detector.result["encoding"]

def loads(content: Union[str, bytes]) -> dict:
    """Take a bytes or str parameter will result a loaded dict JSON"""
    if ORJSON_OK:
        return orjson.loads(content)
    
    return json.loads(content)

def dumps(content: dict, convert_str=True) -> Union[str, bytes]:
    """Take a dict parameter will result in str or bytes 
    (str, if param `convert_str` is True, else bytes)"""
    dumped = None
    if ORJSON_OK:
        dumped = orjson.dumps(content)
    else:
        dumped = json.dumps(content)

    if convert_str and ORJSON_OK:
        # Do technique convert str from bytes
        # because by default, orjson is returning bytes data

        # Get encoding
        encoding = _get_encoding(dumped)

        # Begin the decoding
        return dumped.decode(encoding)
    elif not convert_str and not ORJSON_OK:
        return dumped.encode("utf-8")

    # Return the data as-is
    return dumped
    
    