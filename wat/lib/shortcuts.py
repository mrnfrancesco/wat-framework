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

import logging
import inspect

from wat.lib.properties import Property


def properties(parent, children):
    """It avoids to repeat same code many times when you have to define properties with the same parent.
    The following code is completely equivalent::

        # shortcut version
        properties("aaa.bbb.ccc", ["ee", "ff", "gg"])

        # long version
        Property("aaa.bbb.ccc.ee")
        Property("aaa.bbb.ccc.ff")
        Property("aaa.bbb.ccc.gg")

    :param parent: the common properties parent
    :type parent: str
    :param children: the list of all the properties name with common specified parent
    :type children: list[str]
    :return: a list of `Property` objects with common parent and specified names
    :rtype: list[Property]
    :raise `InvalidTypeError`: if the parent or children type is not the specified one
    """
    return [Property(".".join([parent, child])) for child in children]


def hierlogger(depth=3):
    """
    Provide a logger instance with no need to specify the name, cause it will get it automagically.
    To use it just import the method at module level with

    >>> from wat.lib.shortcuts import hierlogger as logger

    Then use it in whatever level you want (module, function, class or method), e.g.:

    >>> if __name__ == '__main__':
    >>>     logger().info('info message')

    Remember **NOT** to call `logging.basicConfig()`! It should be done by user interface.

    :param depth: the depth level of the provided logger (1: module only, 2: module.class, 3: module.class.method)
    :type depth: int
    :return: a logger object
    :rtype: logging.Logger

    *Thanks to Zaar Hai answer to* `logger chain in python <http://stackoverflow.com/a/3060995/3549503>`_
    *question on stackoverflow!*
    """
    caller_frame = inspect.stack()[1]
    caller = caller_frame[0]
    lname = '__hierlogger%(depth)s__' % {'depth': str(depth)}
    if lname not in caller.f_locals:
        logger_name = str()
        if depth >= 1:
            try:
                logger_name += inspect.getmodule(inspect.stack()[1][0]).__name__
            except:
                pass
        if depth >= 2 and 'self' in caller.f_locals:
            logger_name += ('.' if logger_name else '') + caller.f_locals['self'].__class__.__name__
        if depth >= 3 and caller_frame[3]:
            logger_name += ('.' if logger_name else '') + caller_frame[3]
        logger = logging.getLogger(logger_name)
        logger.addHandler(logging.NullHandler())
        caller.f_locals[lname] = logger
    return caller.f_locals[lname]