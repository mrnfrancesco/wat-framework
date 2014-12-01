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
            self._name = name
        else:
            raise InvalidTypeError(name, (str,))

    def exists(self):
        """Check if the property exists or not.
        :return: True if the property exists, False otherwise
        :rtype: bool
        """
        try:
            __import__('.'.join([wat.packages.components, self._name]))
        except ImportError:
            return False
        return True

    def __repr__(self):
        return "Property('%s')" % self._name

    def __eq__(self, other):
        return isinstance(other, Property) and self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._name)

    def __str__(self):
        return self._name


class Constraint(Property):
    def __init__(self, name, expected, compare_fn='eq'):
        super(Constraint, self).__init__(name)
        self.expected_value = expected
        self.compare_fn = compare_fn

    def compare(self):
        return getattr(Registry.instance()[self._name], '__%s__' % self.compare_fn)(self.expected_value)

    def __repr__(self):
        return "Constraint('%s', '%s', '%s')" % (self._name, self.expected_value, self.compare_fn)

    def __eq__(self, other):
        if isinstance(other, Constraint):
            return self._name == other._name \
                and self.expected_value == other.expected_value \
                and self.compare_fn == other.compare_fn
        elif isinstance(other, Property):
            return self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(other)