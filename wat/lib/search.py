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
from pkgutil import walk_packages, os

from wat.lib.components import iswatcomponent, module_from
import wat
from wat.lib.exceptions import PropertyDoesNotExist


def submoduleof(module):
    for submodule_name in module.__modules__:
        yield '.'.join([module.__name__, submodule_name])


def componentsin(module):
    return filter(
        lambda cls: cls.__module__ == module.__name__ and iswatcomponent(cls),
        [member[1] for member in inspect.getmembers(module, inspect.isclass)]
    )


def search(prop=None, preconditions=None):
    components = list()
    if prop is not None:
        try:
            module = importlib.import_module('.'.join([wat.packages.components, prop]))
            if hasattr(module, '__modules__') and module.__modules__:
                for submodule_name in submoduleof(module):
                    try:
                        submodule = importlib.import_module(submodule_name)
                        components.extend([cls for cls in componentsin(submodule)])
                    except ImportError:
                        continue
        except ImportError:
            raise PropertyDoesNotExist(prop)

    if preconditions is not None:
        # if we have no components, get them all and then filter by preconditions
        # otherwise filter them only
        if not components:
            components = all_components()

        components = filter(
            lambda component_class: not set(str(dep) for dep in component_class.dependencies).isdisjoint(preconditions),
            components
        )
    return components


def all_components():
    components = list()
    paths = [wat.dirs.components]
    for path in paths:
        for _, package_or_path, ispackage in walk_packages(path=[path], prefix=path + os.path.sep):
            if ispackage:
                paths.append(package_or_path)
            else:
                components.extend(componentsin(importlib.import_module(module_from(package_or_path))))
    return components