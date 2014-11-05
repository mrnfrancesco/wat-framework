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

from wat.lib.components import WatComponent, iswatcomponent
from wat.lib.properties import Property, Constraint
from wat.lib.search import search
import wat


def checkdependencies(preconditions):
    resolvable = list()
    for precondition in preconditions:
        # check if property value exists into registry
        # even if no module provide it (e.g. user-given)
        if WatComponent.precondition(str(precondition)) is not None:
            if isinstance(precondition, Constraint):
                if precondition.compare(WatComponent.precondition(str(precondition))):
                    continue
                else:
                    return None, False
            elif isinstance(precondition, Property):
                continue
        else:
            try:
                # Check if python package exists to resolve given precondition
                module = importlib.import_module('.'.join([wat.packages.components, str(precondition)]))
                # Check if provided module is a WAT module or not,
                # if it is, check for submodules entry (there must be at least one)
                if not hasattr(module, '__modules__') or not module.__modules__:
                    return None, False
            except ImportError:
                return None, False
            resolvable.append(precondition)
    # ok, all preconditions are resolved/resolvable
    return resolvable, True


class Node(object):
    def __init__(self, module_class):
        if iswatcomponent(module_class):
            self.module = module_class
        else:
            raise  # TODO: raise a proper exception to say "this is not a WAT Module"

        if self.module.dependencies:  # if there is at least a dependency
            dependencies, resolved_or_resolvable = checkdependencies(self.module.dependencies)
            if resolved_or_resolvable:
                if dependencies:
                    self.nodes = dict((prop, ORNode(prop)) for prop in dependencies)
            else:
                raise  # TODO: raise a proper exception to say "there are some unresolvable dependencies"


class ORNode(object):
    def __init__(self, property_name):
        self.property_name = property_name

        try:
            self.nodes = [Node(module_class=result) for result in search(prop=property_name)]
        except:  # TODO: catch and handle the exception raised by search (?)
            pass
        if not hasattr(self, 'nodes'):
            raise  # TODO: raise a proper exception to say "there are unresolvable dependencies"


def findpaths(properties):
    if isinstance(properties, str):
        properties = list(properties)
    return [ORNode(prop) for prop in properties]


# WatComponent.provide('website.cms.name', 'opencart')
# WatComponent.provide('website.cms.opencart.admin.directory', 'admin')
# n = ORNode('website.cms.opencart.version')
# print n

# from digraphtools import *
#
# dag = graph_from_edges([(1, 2), (2, 3), (3, 4), (2, 4), (4, 5), (5, 3)])
# print dag
# for node in dfs_topsort_traversal(dag, 1):
#     print node

requested_props = ["website.cms.opencart.version"]
to_process_props = requested_props
involved_props = dict()

for processing_property in to_process_props:
    watmodules = search(prop=processing_property)
    for watmodule in watmodules:
        if watmodule.dependencies:
            to_process_props.extend([str(dependency) for dependency in watmodule.dependencies])
    involved_props[processing_property] = watmodules

print "Involved Properties: "
print involved_props

if set(requested_props).issubset(set([key for key, value in involved_props.items() if value])):
    print 'ok'
else:
    print 'ko'