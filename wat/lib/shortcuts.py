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