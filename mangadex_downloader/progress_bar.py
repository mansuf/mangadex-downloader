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

"""
Progress bar manager for volumes, chapters, pages and file sizes
"""

import logging
import sys
from tqdm import tqdm

class ProgressBarManager:
    valid_types_order = [
        "volumes",
        "chapters",
        "pages",
        "file sizes",
        "convert"
    ]

    def __init__(self):
        self._logger = logging.getLogger(__name__)

        # Initialization vars for progress bar (initial and total value)
        self._volumes_initial = self._volumes_total = 0
        self._chapters_initial = self._chapters_total = 0
        self._pages_initial = self._pages_total = 0
        self._file_sizes_initial = self._file_sizes_total = 0
        self._convert_initial = self._convert_total = 0
        
        # Initialization vars for progress bar (unit value)
        self._volumes_unit = "vol"
        self._chapters_unit = "ch"
        self._pages_unit = "page"
        self._file_sizes_unit = "B"
        self._convert_unit = "page"

        # Progress bar main objects
        self._volumes: tqdm = None
        self._chapters: tqdm = None
        self._pages: tqdm = None
        self._file_sizes: tqdm = None
        self._convert: tqdm = None

        # Do the user want to use stacked progress bar ?
        self._stacked = False

        # No progress bar ?
        self._disabled = False

        # Dummy logger
        self._dummy_logger = logging.getLogger("dummy_logger")
        self._dummy_logger.addHandler(logging.NullHandler())

        # Types order
        self.set_types_order(*self.valid_types_order)

        # Progress bars that are only allowed to showed up
        # if stacked mode is not enabled
        self._single_progress_bar_types = [
            "_file_sizes",
            "_convert"
        ]

    def _create_progress_bar(self, var_name: str) -> tqdm:
        var: tqdm = getattr(self, var_name)
        if var:
            var.close()

        # Remove "_" in the front and replace "_" with whitespace and capitalize it
        desc_name = var_name[1:].replace("_", " ").capitalize()

        kwargs_tqdm = {
            "initial": getattr(self, f"{var_name}_initial"),
            "total": getattr(self, f"{var_name}_total"),
            "unit": getattr(self, f"{var_name}_unit"),
            "unit_scale": True,
        }

        # Determine ncols progress bar
        length = len(desc_name)
        if length < 20:
            kwargs_tqdm.setdefault('ncols', 80)
        elif length > 20 and length < 50:
            kwargs_tqdm.setdefault('dynamic_ncols', True)
        # Length desc is more than 40 or 50
        elif length >= 50:
            desc_name = desc_name[:20] + '...'
            kwargs_tqdm.setdefault('ncols', 90)

        kwargs_tqdm.setdefault('desc', desc_name)

        return tqdm(**kwargs_tqdm)

    def _create_stacked_progress_bars(self):
        """Create stacked progress bars based on types order"""
        for name_var in self._types_order:
            pb = self._create_progress_bar(name_var)
            setattr(self, name_var, pb)

    def _create_dummy_progress_bar(self):
        return tqdm(disable=True)

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value

    @property
    def stacked(self):
        return self._stacked
    
    @stacked.setter
    def stacked(self, value: bool):
        self._stacked = value

    def _get_progress_bar(self, var, recreate=False) -> tqdm:
        if self.disabled:
            # Well the progress bar is disabled
            # What are you gonna do ? 
            return self._create_dummy_progress_bar()

        value_var = getattr(self, var)

        # If stacked progress bar is not enabled
        # DO NOT ALLOW  PROGRESS BARS (except file_sizes) TO BE CREATED
        if not self.stacked and var not in self._single_progress_bar_types:
            return self._create_dummy_progress_bar()
        elif var not in self._types_order:
            # Some type are not in order
            # Create dummy progress bar instead
            return self._create_dummy_progress_bar()

        if value_var is None or recreate:
            if self.stacked:
                self._create_stacked_progress_bars()
            else:
                value_var = self._create_progress_bar(var)
                setattr(self, var, value_var)
        
        value_var = getattr(self, var)

        return value_var

    def get_volumes_pb(self, recreate=False):
        """Get progress bar for volumes"""
        return self._get_progress_bar("_volumes", recreate)

    def get_chapters_pb(self, recreate=False):
        return self._get_progress_bar("_chapters", recreate)

    def get_pages_pb(self, recreate=False):
        return self._get_progress_bar("_pages", recreate)

    def get_file_sizes_pb(self, recreate=False):
        return self._get_progress_bar("_file_sizes", recreate)

    def get_convert_pb(self, recreate=False):
        return self._get_progress_bar("_convert", recreate)

    # Initial value for tqdm kwargs

    def set_volumes_initial(self, value: int):
        if self._volumes is not None:
            self._volumes.initial = value
            self._volumes.refresh()

        self._volumes_initial = value
    
    def set_chapters_initial(self, value: int):
        if self._chapters is not None:
            self._chapters.initial = value
            self._chapters.refresh()

        self._chapters_initial = value

    def set_pages_initial(self, value: int):
        if self._pages is not None:
            self._pages.initial = value
            self._pages.refresh()

        self._pages_initial = value

    def set_file_sizes_initial(self, value: int):
        if self._file_sizes is not None:
            self._file_sizes.initial = value
            self._file_sizes.refresh()

        self._file_sizes_initial = value

    def set_convert_initial(self, value: int):
        if self._convert is not None:
            self._convert.initial = value
            self._convert.refresh()

        self._convert_initial = value

    # Total value for tqdm kwargs

    def set_volumes_total(self, value: int):
        if self._volumes is not None:
            self._volumes.total = value
            self._volumes.refresh()

        self._volumes_total = value

    def set_chapters_total(self, value: int):
        if self._chapters is not None:
            self._chapters.total = value
            self._chapters.refresh()

        self._chapters_total = value

    def set_pages_total(self, value: int):
        if self._pages is not None:
            self._pages.total = value
            self._pages.refresh()

        self._pages_total = value

    def set_file_sizes_total(self, value: int):
        if self._file_sizes is not None:
            self._file_sizes.total = value
            self._file_sizes.refresh()

        self._file_sizes_total = value

    def set_convert_total(self, value: int):
        if self._convert is not None:
            self._convert.total = value
            self._convert.refresh()
        
        self._convert_total = value

    # Close progress bar

    def close_all(self):
        """Close all progress bars"""
        for var_name in self._types_order:
            var: tqdm = getattr(self, var_name)
            if var is not None:
                var.close()
                setattr(self, var_name, None)

    # Logger configurations

    @property
    def logger(self):
        if self.stacked:
            # We do not want to show the logger
            # If stacked progress bar is on
            return self._dummy_logger

        return self._logger

    def set_logger_level(self, level):
        self._logger.setLevel(level)

    def set_types_order(self, *types):
        values = []
        for _type in types:
            values.append("_%s" % _type.replace(" ", "_"))

        self._types_order = values

progress_bar_manager = ProgressBarManager()