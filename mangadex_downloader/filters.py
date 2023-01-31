# MIT License

# Copyright (c) 2022 Rahman Yusuf

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

import re
from dataclasses import dataclass
from typing import Callable

from .errors import MangaDexException, InvalidURL
from .utils import validate_url
from .config.utils import validate_bool, ConfigTypeError
from .manga import ContentRating
from .language import get_language
from .tag import get_all_tags

class FilterError(MangaDexException):
    def __init__(self, key, msg):
        text = f"Filter error '{key}', {msg}"

        super().__init__(text)

@dataclass
class _FilterKey:
    param_name: str
    validator: Callable

# Help me bruh
# Why i'm making this
class Filter:
    def __init__(self, allowed_keys=None):
        self.filters = {}
        self.tags = self._get_tags()

        self._init_filters()

        self.allowed_keys = allowed_keys

    def get_request_params(self, **filters):
        params = {}
        for filter_key, filter_value in filters.items():
            if self.allowed_keys and filter_key not in self.allowed_keys:
                raise FilterError(filter_key, "Invalid key filter")

            try:
                f: _FilterKey = self.filters[filter_key]
            except KeyError:
                raise FilterError(filter_key, "Invalid key filter")

            # Special treatment for "order[...]" filters
            if 'order' in filter_key:
                filter_value = f.validator(filter_value)
                params.update(**filter_value)
            else:
                params[f.param_name] = f.validator(filter_value)

        # Enable pornographic content rating on default
        try:
            params['contentRating[]']
        except KeyError:
            params['contentRating[]'] = [i.value for i in ContentRating]

        return params

    def _get_tags(self):
        tags = {}

        for tag in get_all_tags():
            tags[tag.name.lower()] = tag

        return tags

    def _init_filters(self):
        self.filters.update({
            'year': _FilterKey(
                'year',
                self._validate_year,
            ),
            'authors': _FilterKey(
                'authors[]',
                self._dummy_validator,
            ),
            'artists': _FilterKey(
                'artists[]',
                self._dummy_validator,
            ),
            'author_or_artist': _FilterKey(
                'authorOrArtist',
                lambda x: self._validate_uuid("author_or_artist", x),
            ),
            'included_tags': _FilterKey(
                'includedTags[]',
                lambda x: self._validate_tags("included_tags", x),
            ),
            'included_tags_mode': _FilterKey(
                'includedTagsMode',
                lambda x: self._validate_tags_mode("included_tags_mode", x),
            ),
            'excluded_tags': _FilterKey(
                'excludedTags[]',
                lambda x: self._validate_tags("excluded_tags", x),
            ),
            'excluded_tags_mode': _FilterKey(
                'excludedTagsMode',
                lambda x: self._validate_tags_mode("excluded_tags_mode", x),
            ),
            'status': _FilterKey(
                'status[]',
                lambda x: self._validate_values_from_list(
                    "status",
                    x,
                    [
                        "ongoing",
                        "completed",
                        "hiatus",
                        "cancelled"
                    ]
                )
            ),
            'original_language': _FilterKey(
                "originalLanguage[]",
                lambda x: self._validate_language("original_language", x)
            ),
            'excluded_original_language': _FilterKey(
                'excludedOriginalLanguage[]',
                lambda x: self._validate_language("excluded_original_language", x)
            ),
            'available_translated_language': _FilterKey(
                'availableTranslatedLanguage[]',
                lambda x: self._validate_language("available_translated_language", x)
            ),
            'publication_demographic': _FilterKey(
                'publicationDemographic[]',
                lambda x: self._validate_values_from_list(
                    "publication_demographic",
                    x,
                    [
                        "shounen",
                        "shoujo",
                        "josei",
                        "seinen",
                        "none"
                    ]
                )
            ),
            'content_rating': _FilterKey(
                "contentRating[]",
                lambda x: self._validate_values_from_list(
                    "content_rating",
                    x,
                    [a.value for a in ContentRating]
                )
            ),
            'created_at_since': _FilterKey(
                "createdAtSince",
                self._dummy_validator
            ),
            'updated_at_since': _FilterKey(
                "updatedAtSince",
                self._dummy_validator
            ),
            'has_available_chapters': _FilterKey(
                'hasAvailableChapters',
                self._validate_has_chapters
            ),
            'group': _FilterKey(
                "group",
                lambda x: self._validate_uuid("group", x)
            ),
            'order': _FilterKey(
                'order',
                self._validate_order
            )
        })

    def _validate_year(self, value):
        if value:
            m = re.match(r'[0-9]{4}', value)
            if not m:
                raise FilterError(
                    "year",
                    f"value must be integer and length must be 4"
                )
        
        return value

    def _dummy_validator(self, value):
        return value

    def _validate_tags(self, key, values):
        new_values = []
        if values is None:
            return

        if isinstance(values, str):
            values = [values]

        # Lowercase to prevent error
        values = [i.lower() for i in values]

        for value in values:
            # Try to match the keyword tags
            try:
                tag = self.tags[value]
            except KeyError:
                pass
            else:
                new_values.append(tag.id)
                continue

            # Try to get uuid
            try:
                _id = validate_url(value)
            except InvalidURL:
                raise FilterError(
                    key,
                    f"'{value}' is not valid keyword or uuid tag"
                )
            
            new_values.append(_id)
        
        return new_values

    def _validate_tags_mode(self, key, value):
        value_and_or = ['AND', 'OR']
        if value and value.upper() not in value_and_or:
            raise FilterError(
                key,
                f"value must be 'OR' or 'AND', not '{value}'"
            )
        
        return value

    def _validate_values_from_list(self, key, values, array):
        if values is None:
            return
        
        if isinstance(values, str):
            values = [values]

        for value in values:
            if value.lower() not in array:
                raise FilterError(
                    key,
                    f"Value must be one of {array}, not {value}"
                )

        return values

    def _validate_language(self, key, values):
        new_values = []
        if values is None:
            return

        if isinstance(values, str):
            values = [values]

        for value in values:
            try:
                lang = get_language(value)
            except ValueError as e:
                raise FilterError(key, e)
            else:
                new_values.append(lang.value)
    
        return new_values

    def _validate_has_chapters(self, value):
        if value:
            try:
                validate_bool(value)
            except ConfigTypeError as e:
                raise FilterError("has_available_chapters", e)
        
        return value

    def _validate_uuid(self, key, values):
        new_values = []
        if values is None:
            return
        
        if isinstance(values, str):
            values = [values]
        
        for value in values:
            # Get the id
            try:
                _id = validate_url(value)
            except InvalidURL:
                raise FilterError(
                    key,
                    f"'{value}' is not valid UUID"
                )
            else:
                new_values.append(_id)
        
        return new_values

    def _validate_order(self, order):
        new_order = {}
        ascending = ['asc', 'ascending']
        descending = ['desc', 'descending']
        for key, value in order.items():
            # Validate order keys
            re_order_key = r'order\[(' \
                        r'title|' \
                        r'year|' \
                        r'createdAt|' \
                        r'updatedAt|' \
                        r'latestUploadedChapter|' \
                        r'followedCount|' \
                        r'relevance|' \
                        r'rating|' \
                        r')\]'
            match = re.match(re_order_key, key)
            if match is None:
                raise FilterError(
                    key,
                    "Invalid order key"
                )

            if value in ascending:
                new_order[key] = ascending[0]
            elif value in descending:
                new_order[key] = descending[0]
            else:
                raise FilterError(
                    key,
                    f"invalid value must be one of {ascending} or {descending}"
                )
        
        return new_order