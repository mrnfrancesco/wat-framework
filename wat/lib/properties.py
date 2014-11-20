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

__all__ = ['Registry', 'Property', 'Constraint']

from singleton.singleton import Singleton

import wat
from wat.lib.exceptions import InvalidTypeError


@Singleton
class Registry(dict):
    """A singleton dictionary to store components provided properties and to solve components preconditions."""


class Property(object):
    def __init__(self, name):
        """Create an instance of the property with the specified name to use in module specification.
        :param name: the name of the property to represent.
        :type name: str
        :raise InvalidTypeError: if the parameter is not a string
        """
        if isinstance(name, str):
            self.name = name
        else:
            raise InvalidTypeError(name, (str,))

    def exists(self):
        """Check if the property exists or not.
        :return: True if the property exists, False otherwise
        :rtype: bool
        """
        try:
            __import__('.'.join([wat.packages.components, self.name]))
        except ImportError:
            return False
        return True

    def __repr__(self):
        return "Property('%s')" % self.name

    def __eq__(self, other):
        return isinstance(other, Property) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Constraint(Property):
    def __init__(self, name, expected, compare_fn='eq'):
        super(Constraint, self).__init__(name)
        if expected is not None:
            self.expected_value = expected
        self.compare_fn = compare_fn

    def compare(self):
        return getattr(Registry.instance()[self.name], '__%s__' % self.compare_fn)(self.expected_value)
