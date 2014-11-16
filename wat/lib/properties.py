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
import wat

__all__ = ['Registry', 'Property', 'Constraint']

from singleton.singleton import Singleton

from wat.lib.exceptions import PropertyDoesNotExist, InvalidTypeError


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

    def __repr__(self):
        return "Property('%s')" % self.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Constraint(Property):
    def __init__(self, name, expected, compare='eq'):
        super(Constraint, self).__init__(name)
        if expected is not None:
            self.expected_value = expected
        self.compare = lambda value: getattr(str(value), '__%s__' % compare)(self.expected_value)


def properties(parent, children):
    """It is just a shortcut to avoid repeat same code many times in cases in which you have the same parent
    for many children.
    The following code is completely equivalent::

        #short version
        properties("aaa.bbb.ccc", ["ee", "ff", "gg"])

        #long version
        Property("aaa.bbb.ccc.ee")
        Property("aaa.bbb.ccc.ff")
        Property("aaa.bbb.ccc.gg")

    :param parent: the common properties parent
    :type parent: str
    :param children: the list of all the properties name with common specified parent
    :type children: list[str]
    :return: a list of `Property` objects with common parent and specified names
    :rtype: list[Property]
    :raise `PropertyNameSyntaxError`: if at least one of the resulting property name
                                    is not compliance with choosen naming convention
    """
    return [Property(".".join([parent, child])) for child in children]