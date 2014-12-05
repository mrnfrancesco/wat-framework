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

import sys
import traceback
from os.path import join
from datetime import datetime

from wat import dirs
from wat.lib.shortcuts import hierlogger as logger


def excepthook(exc_type, exc_message, exc_traceback):
    logger(depth=1).critical(
        "Unhandled '%(exc_type)s' was raised: %(exc_message)s" % {
            'exc_type': exc_type.__name__,
            'exc_message': exc_message
        }
    )

    try:
        with open(join(dirs.install, 'errors.log'), mode='a') as f:
            f.write('-' * 30 + str(datetime.now()) + '-' * 30 + '\n')
            traceback.print_exception(exc_type, exc_message, exc_traceback, file=f)
    except IOError:
        pass


sys.excepthook = excepthook