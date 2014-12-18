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
from wat.lib.exceptions import InvalidTypeError


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


def components(postconditions=None, preconditions=None):
    components = __components()
    # no filters means all components
    if postconditions is None and preconditions is None:
        return components
    else:
        if postconditions is not None:
            if not isinstance(postconditions, (list, set, tuple)):
                raise InvalidTypeError(postconditions, (list, set, tuple))
        if preconditions is not None:
            if not isinstance(preconditions, (list, set, tuple)):
                raise InvalidTypeError(preconditions, (list, set, tuple))
            elif isinstance(preconditions, (list, tuple)):
                preconditions = set(preconditions)

    if postconditions is not None:
        # take all the components which give the specified postconditions
        components = filter(
            lambda component: str(component.postcondition) in postconditions,
            components
        )

    if preconditions is not None:
        # take all the components which require at least one of the specified precondition
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
            lambda prop: not any(search_term in prop for search_term in not_containing),
            properties
        )

    return properties