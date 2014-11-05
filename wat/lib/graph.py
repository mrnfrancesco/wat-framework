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

from wat.lib.components import WatComponent
from wat.lib.properties import Property, Constraint
import wat


def checkpreconditions(preconditions):
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