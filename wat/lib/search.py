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

__all__ = {'components', 'properties'}

import importlib
import inspect
from pkgutil import walk_packages, os

import wat
from wat.lib.components import iswatcomponent, component_from
from wat.lib.exceptions import PropertyDoesNotExist, InvalidTypeError


def __submoduleof(module):
    for submodule_name in module.__modules__:
        yield '.'.join([module.__name__, submodule_name])


def __componentsin(module):
    return filter(
        lambda cls: cls.__module__ == module.__name__ and iswatcomponent(cls),
        [member[1] for member in inspect.getmembers(module, inspect.isclass)]
    )


def __components():
    components = list()
    paths = [wat.dirs.components]
    for path in paths:
        for _, package_or_path, ispackage in walk_packages(path=[path], prefix=path + os.path.sep):
            if ispackage:
                paths.append(package_or_path)
            else:
                components.extend(__componentsin(importlib.import_module(component_from(package_or_path))))

    return components


def components(postcondition=None, preconditions=None):
    # no filters means all components
    if postcondition is None and preconditions is None:
        return __components()
    else:
        if postcondition is not None:
            if not isinstance(postcondition, str):
                raise InvalidTypeError(postcondition, (str,))
        if preconditions is not None:
            if not isinstance(preconditions, (list, set, tuple)):
                raise InvalidTypeError(preconditions, (list, set, tuple))
            elif isinstance(preconditions, (list, tuple)):
                preconditions = set(preconditions)

    components = list()
    if postcondition is not None:
        # take all the components which give the specified postcondition
        try:
            module = importlib.import_module('.'.join([wat.packages.components, postcondition]))
            if hasattr(module, '__modules__') and module.__modules__:
                for submodule_name in __submoduleof(module):
                    try:
                        submodule = importlib.import_module(submodule_name)
                        components.extend([cls for cls in __componentsin(submodule)])
                    except ImportError:
                        continue
        except ImportError:
            raise PropertyDoesNotExist(postcondition)

    if preconditions is not None:
        # if we have no postcondition filter, get all the components
        # then filter by preconditions, otherwise filter them only
        if postcondition is None:
            components = __components()

        components = filter(
            lambda component: not set(str(dep) for dep in component.preconditions).isdisjoint(preconditions),
            components
        )
    return components


def __properties():
    properties = set()
    for component in __components():
        properties.add(str(component.postcondition))
        for prop in component.preconditions:
            properties.add(str(prop))

    return properties


def properties(containing=None, not_containing=None):
    if containing is not None:
        if not isinstance(containing, (list, set, tuple)):
            raise InvalidTypeError(containing, (list, set, tuple))
    if not_containing is not None:
        if not isinstance(not_containing, (list, set, tuple)):
            raise InvalidTypeError(not_containing, (list, set, tuple))

    properties = __properties()

    if containing is not None:
        properties = filter(
            lambda prop: any(search_term in prop for search_term in containing),
            properties
        )

    if not_containing is not None:
        properties = filter(
            lambda prop: not any(search_term in prop for search_term in containing),
            properties
        )

    return properties