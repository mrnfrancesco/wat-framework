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

import importlib
import inspect

from it.mrnfrancesco.framework import wat
from it.mrnfrancesco.framework.wat.lib.modules import MetaModule, WatModule


def iswatmodule(module_class):
    """
    :param module_class: the class of the module you want to know if it is a Wat module
    :type module_class: class
    :rtype: bool
    :return: `True` if the specified module class is a Wat module, `False` otherwise
    """
    return WatModule in module_class.__bases__ and isinstance(module_class, MetaModule)


def submoduleof(module):
    for submodule_name in module.__modules__:
        yield '.'.join([module.__name__, submodule_name])


def watmodulein(module):
    return filter(
        lambda elem: elem.__module__ == module.__name__ and iswatmodule(elem),
        [member[1] for member in inspect.getmembers(module, inspect.isclass)]
    )


class ANDNode(object):

    def __init__(self, properties):
        self.nodes = dict((prop, ORNode(prop)) for prop in properties)

    def __sort__(self):
        # TODO: implement default sort method
        pass


class ORNode(object):

    def __init__(self, property_name):
        self.property_name = property_name

        self.nodes = []
        module = importlib.import_module("{}.{}".format(wat.package.modules, property_name))
        for submodule_name in submoduleof(module):
            submodule = importlib.import_module(submodule_name)
            self.nodes += watmodulein(submodule)

    def __sort__(self):
        # TODO: implement default sort method
        pass