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

__all__ = ['Singleton']


class Singleton(object):
    """
    The Singleton design pattern implementation as class decorator.
    Its usage is simpe, just put @Singleton decorator over the class
    definition you want to make a singleton and then use the
    class as usual::

        @Singleton
        class WhateverClassDefinition(object):
                pass

        wcd = WhateverClassDefinition()
    """
    def __init__(self, cls):
        """
        :param cls: decorator class type
        """
        self.__cls = cls
        # make sure errors do not use 'Singleton' as class name
        self.__class__.__name__ = cls.__name__
        self.__instance = None

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = self.__cls(*args, **kwargs)
        return self.__instance