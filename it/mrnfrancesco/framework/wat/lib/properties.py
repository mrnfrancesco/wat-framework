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

__all__ = ['Property', 'Constraint', 'Operation']

import re

from it.mrnfrancesco.framework.wat.lib.exceptions import InvalidPropertyError, EmptyValueError


class Property(object):

    __NAME_PATTERN = re.compile(r'^(?:(?:[a-z]+[a-z0-9_]*[a-z0-9]+)\.)*(?:[a-z]+[a-z0-9_]*[a-z0-9]+)$')

    def __init__(self, name):
        """Create an instance of the property with the specified name to use in module specification.

        :param name: the name of the property to represent.
        :raise PropertyNameSyntaxError: if the property name is not compliance with choosen naming convention.
        """
        if Property.__NAME_PATTERN.match(name):
            self.name = name
        else:
            raise InvalidPropertyError(name)

    def __str__(self):
        if hasattr(self, 'value') and self.value:
            return "%s=%s" % (self.name, self.value)
        else:
            return self.name


class Operation(Property):

    def __init__(self, name, params):
        super(Operation, self).__init__(name)
        if params:
            self.params = params
        else:
            raise EmptyValueError("params", params)


class Constraint(Property):

    def __init__(self, name, expected, compare='eq'):
        super(Constraint, self).__init__(name)
        if expected is not None:
            self.expected_value = expected
        self.compare = compare


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