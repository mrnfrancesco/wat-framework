# WAT Framework, make simple to do the complex
# Copyright 2014 Francesco Marano and individual contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = {'config'}

import logging
import colorama
from colorama import Back, Fore, Style


def config(colored=True, debugging=False, level='info', filename=None):
    import logging
    from logging.config import dictConfig

    handler = {
        'formatter': 'debugging' if debugging else 'default'
    }
    if filename is None:
        handler['class'] = 'wat.ui.cli.log._ColorStreamHandler' if colored else 'logging.StreamHandler'
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
                'format': "[%(levelname)-8s]\t%(message)s",
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


class _ColorStreamHandler(logging.StreamHandler):

    DEFAULT = Style.RESET_ALL
    CRITICAL = Back.RED
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.GREEN
    DEBUG = Fore.MAGENTA

    colorama.init(autoreset=True)

    def format(self, record):
        text = logging.StreamHandler.format(self, record)
        color = getattr(_ColorStreamHandler, record.levelname, _ColorStreamHandler.DEFAULT)
        return color + text