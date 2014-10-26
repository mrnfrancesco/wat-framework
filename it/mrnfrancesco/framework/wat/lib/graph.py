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

import inspect
import importlib

from it.mrnfrancesco.framework import wat
from it.mrnfrancesco.framework.wat.lib.modules import MetaModule, WatModule
from it.mrnfrancesco.framework.wat.lib.properties import Property, Constraint, Operation


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


def checkdependencies(dependencies):
    resolvable = list()
    for dependency in dependencies:
        # check if property value exists into registry
        # even if no module provide it (e.g. user-given)
        if WatModule.getdependency(str(dependency)) is not None:
            if isinstance(dependency, Constraint):
                if dependency.compare(WatModule.getdependency(str(dependency))):
                    continue
                else:
                    return None, False
            elif isinstance(dependency, Operation):
                raise NotImplementedError  # TODO: implement also this
            elif isinstance(dependency, Property):
                continue
            else:
                raise ValueError  # TODO: raise a proper exception with custom message
        else:
            try:
                # Check if python package exists to resolve given dependency
                module = importlib.import_module('.'.join([wat.package.modules, str(dependency)]))
                # Check if provided module is a WAT module or not,
                # if it is, check for submodules entry (there must be at least one)
                if not hasattr(module, '__modules__') or not module.__modules__:
                    return None, False
            except ImportError:
                return None, False
            resolvable.append(dependency)
    # ok, all dependencies are resolved/resolvable
    return resolvable, True


class Node(object):

    def __init__(self, module_class):
        if iswatmodule(module_class):
            self.module = module_class
        else:
            raise  # TODO: raise a proper exception to say "this is not a WAT Module"

        if self.module.dependencies:  # if there is at least a dependency
            dependencies, resolved_or_resolvable = checkdependencies(self.module.dependencies)
            if resolved_or_resolvable:
                if dependencies:
                    self.nodes = dict((prop, ORNode(prop)) for prop in self.module.dependencies)
            else:
                raise  # TODO: raise a proper exception to say "there are some unresolvable dependencies"


class ORNode(object):

    def __init__(self, property_name):
        self.property_name = property_name

        self.nodes = list()
        try:
            module = importlib.import_module("{}.{}".format(wat.package.modules, property_name))
        except ImportError:
            raise  # TODO: wrap ImportError and re-raise in a custom exception
        for submodule_name in submoduleof(module):
            try:
                submodule = importlib.import_module(submodule_name)
                self.nodes.extend([Node(cls) for cls in watmodulein(submodule)])
            except ImportError:
                continue
        if not self.nodes:
            raise  # TODO: raise a proper exception to say "there are unresolvable dependencies"


def findpaths(properties):
    if isinstance(properties, str):
        properties = list(properties)
    return [ORNode(prop) for prop in properties]


