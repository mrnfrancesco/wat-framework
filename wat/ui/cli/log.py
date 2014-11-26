# WAT Framework, make simple to do the complex
# Copyright (C) 2014  Francesco Marano and individual contributors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = {'ColorStreamHandler', 'config'}

import logging


def config(colored=True, debugging=False, level='info', filename=None):
    import logging
    from logging.config import dictConfig

    handler = {
        'formatter': 'debugging' if debugging else 'default'
    }
    if filename is None:
        handler['class'] = 'wat.ui.cli.log.ColorStreamHandler' if colored else 'logging.StreamHandler'
        handler['stream'] = 'ext://sys.stdout'
    else:
        handler['class'] = 'logging.FileHandler'
        handler['filename'] = str(filename)
        handler['mode'] = 'w'

    dictConfig({
        # the version of the logging configuration dictionary
        'version': 1,
        # whether the configuration is to be interpreted as incremental to the existing configuration.
        'incremental': False,
        # whether any existing loggers are to be disabled.
        'disable_existing_loggers': True,
        'formatters': {
            'debugging': {
                'format': "[%(asctime)s]\t%(levelname)-8s\t%(name)s:%(lineno)d -> %(message)s",
                'datefmt': "%H:%M:%S"
            },
            'default': {
                'format': "[%(levelname)s]\t%(message)s",
            }
        },
        'handlers': {
            'custom': handler
        },
        'root': {
            'propagate': True,
            'level': getattr(logging, level.upper(), logging.INFO),
            'handlers': ['custom']
        }
    })


# colored stream handler for python logging framework (use the ColorStreamHandler class).
# based on:
# http://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output/1336640#1336640

# Copyright (c) 2014 Markus Pointner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

class _AnsiColorStreamHandler(logging.StreamHandler):
    DEFAULT = '\x1b[0m'  # clears all colors and styles
    CRITICAL = '\x1b[41m'  # red background
    ERROR = '\x1b[31m'  # red
    WARNING = '\x1b[33m'  # yellow
    INFO = '\x1b[32m'  # blue
    DEBUG = '\x1b[35m'  # magenta (purple)

    def format(self, record):
        text = logging.StreamHandler.format(self, record)
        color = getattr(_AnsiColorStreamHandler, record.levelname, _AnsiColorStreamHandler.DEFAULT)
        return color + text + _AnsiColorStreamHandler.DEFAULT


class _WinColorStreamHandler(logging.StreamHandler):
    # wincon.h
    FOREGROUND_BLACK = 0x0000
    FOREGROUND_BLUE = 0x0001
    FOREGROUND_GREEN = 0x0002
    FOREGROUND_CYAN = 0x0003
    FOREGROUND_RED = 0x0004
    FOREGROUND_MAGENTA = 0x0005
    FOREGROUND_YELLOW = 0x0006
    FOREGROUND_GREY = 0x0007
    FOREGROUND_INTENSITY = 0x0008  # foreground color is intensified.
    FOREGROUND_WHITE = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED

    BACKGROUND_BLACK = 0x0000
    BACKGROUND_BLUE = 0x0010
    BACKGROUND_GREEN = 0x0020
    BACKGROUND_CYAN = 0x0030
    BACKGROUND_RED = 0x0040
    BACKGROUND_MAGENTA = 0x0050
    BACKGROUND_YELLOW = 0x0060
    BACKGROUND_GREY = 0x0070
    BACKGROUND_INTENSITY = 0x0080  # background color is intensified.

    DEFAULT = FOREGROUND_WHITE | BACKGROUND_BLACK
    CRITICAL = BACKGROUND_RED | FOREGROUND_WHITE
    ERROR = FOREGROUND_RED
    WARNING = FOREGROUND_YELLOW
    INFO = FOREGROUND_GREEN
    DEBUG = FOREGROUND_MAGENTA

    def _set_color(self, code):
        import ctypes
        ctypes.windll.kernel32.SetConsoleTextAttribute(self._outhdl, code)

    def __init__(self, stream=None):
        logging.StreamHandler.__init__(self, stream)
        # get file handle for the stream
        import ctypes
        import ctypes.util

        crtname = ctypes.util.find_msvcrt()
        crtlib = ctypes.cdll.LoadLibrary(crtname)
        self._outhdl = crtlib._get_osfhandle(stream.fileno())

    def emit(self, record):
        color = getattr(_WinColorStreamHandler, record.levelname, _WinColorStreamHandler.DEFAULT)
        self._set_color(color)
        logging.StreamHandler.emit(self, record)
        self._set_color(_WinColorStreamHandler.DEFAULT)

# select ColorStreamHandler based on platform
import platform

if platform.system() == 'Windows':
    ColorStreamHandler = _WinColorStreamHandler
else:
    ColorStreamHandler = _AnsiColorStreamHandler