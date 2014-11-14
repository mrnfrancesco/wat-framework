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

from wat.lib import components, search
from wat.lib.components import WatComponent
from wat.lib.exceptions import PropertyDoesNotExist, InvalidTypeError
from wat.lib.properties import Property


class RelaxedGraphPlan(object):
    """It is a relaxed version of the GraphPlan algorithm, to represent the planning problem to build a components chain
     to achieve the goal from a specified initial state.

    In particular it is a graph *G=(V,E)* where:

    V = P0 U A1 U P1 U ... U An U Pn with:

        * Pi, state property layer
        * Aj, action layer
        * P0, initial state
        * Pi = {p: p in Pi-1} U {p: exists a in Ai [p=postcondition(a)]}
        * Aj = {a: preconditions(a) is subset of Pj-1}

    E = {(p,a) with p in Pi-1, a in Ai if p in preconditions(a)} U {(a,p) with a in Ai, p in Pi if p=postcondition(a)}
    """

    class ActionLayer(object):
        """Represent an Action Layer for the Relaxed GraphPlan algorithm.
        It is like a *step* into the contruction of the graph and it contains all the actions (framework components)
        with solved dependencies.
        All the contained actions are framework components class type, so they could be give you their preconditions
        and postcondition to automagically represent also the "*missing*" Relaxed GraphPlan Property Layer.
        """

        class NoOpAction(object):
            """Represent a No-Operation action in a Relaxed Graphplan Action Layer.
            It means that it is an action that do nothing and has the same
            precondition and postcondition equals to the specified property.

            **Briefly**: No-Op for property *p* is an action *a* such that *precondition(a)=postcondition(a)=p*
            """

            def __init__(self, prop):
                """Initialize the No-Operation action with the specified property.
                :param prop: the property to bring forward through the NoOp node
                :type prop: Property
                :raise InvalidTypeError: if the specified property is not of type Property or subclasses
                """
                if isinstance(prop, Property):
                    self.preconditions = self.postconditions = {prop}
                else:
                    raise InvalidTypeError(prop, expected=Property)

        def __init__(self, actions=None):
            """Initialize an Action Layer from the specified actions which should be all wat components.
            :param actions: the actions to add in the action layer
            :type actions: set|list|tuple|None
            :raise InvalidTypeError: if actions parameter is not one of the allowed types
            :raise: if at least one action is not a wat component
            """
            if isinstance(actions, (list, set, tuple)):
                if not isinstance(actions, set):
                    actions = set(actions)
                self.actions = set()
                for action in actions:
                    self.add(action)
            elif actions is None:
                self.actions = set()
            else:
                raise InvalidTypeError(actions, (list, set, tuple, type(None)))

        def __len__(self):
            """Return the number of actions in the action layer"""
            return len(self.actions)

        def add(self, action):
            if components.iswatcomponent(action):
                self.actions.add(action)
            else:
                raise  # TODO: raise an "invalid action error"

        def remove(self, action):
            self.actions.discard(action)

        @property
        def preconditions(self):
            """Return all the preconditions needed for the actions in the action layer.
            :rtype: set
            """
            preconditions = set()
            for action in self.actions:
                preconditions = preconditions.union(action.preconditions)
            return preconditions

        @property
        def postconditions(self):
            """Return all the postconditions gained by the actions in the action layer.
            :rtype: set
            """
            return set(Property(action.postcondition) for action in self.actions)

        @property
        def property_layer(self):
            """Return the property layer defined by the action layer.
            It is represented as the ensamble of properties that are available after actual action layer run.
            :rtype: set
            """
            return self.preconditions.union(self.postconditions)

    def __init__(self, initial_state=None, goal_state=None, fail_on_invalid=False):
        """Initialize the graph to build a layered plan as solution of the specified planning problem.

        :param initial_state: all the <property, value> pair to set as initial state
        :type initial_state: list|set|tuple

        :param goal_state: all the properties you want to achieve
        :type goal_state: list|set|tuple

        :param fail_on_invalid: specify if the initialization have to fail on invalid input (set it to True) or it simply ignore the invalid input and go ahead (set it to False). **Default** is *False*.
        :type fail_on_invalid: bool

        :raise: If the initial state or goal state are not of the required type
        :raise: If there is at least an invalid initial state or goal state and *fail_on_invalid* is set to True
        """
        # Check and register initial state
        filtered_initial_state = set()
        if isinstance(initial_state, (list, set, tuple)):
            if all(isinstance(prop_value, tuple) and len(prop_value) == 2 for prop_value in initial_state):
                differences = set()
                for prop, value in initial_state:
                    if isinstance(prop, Property):
                        WatComponent.register({str(prop): value})
                        filtered_initial_state.add(prop)
                    else:
                        differences.add(prop)
                if fail_on_invalid and differences:
                    raise  # TODO: raise an error with differences in it
                elif differences:
                    pass  # TODO: log the differences from the two enambles
                self.__initial_state = filtered_initial_state
            else:
                raise  # TODO: raise "only pair tuple accepted"
        elif initial_state is None:
            self.__initial_state = None  # it's ok to have no user-provided properties
        else:
            raise  # TODO: raise "invalid type"

        # Check and register goal state
        if isinstance(goal_state, (list, set, tuple)):
            filtered_goal_state = set()
            goal_state_errors = set()
            for prop in goal_state:
                try:
                    filtered_goal_state.add(Property(prop))
                except PropertyDoesNotExist:
                    goal_state_errors.add(prop)
            if fail_on_invalid and goal_state_errors:
                raise  # TODO: raise all collected goal state errors
            elif goal_state_errors:
                pass  # TODO: log all collected goal state errors
            self.__goal_state = filtered_goal_state
        elif goal_state is None:
            # It means that you want to see what properties you can
            # achieve with the given properties as initial state
            self.__goal_state = None

        self.__uncollected_actions = set(search.all_components())
        self.__collected_actions = set()  # it collects all the already seen components to avoid loops

        self.__action_layers = list()

        # make the first step to build the first action layer
        initial_action_layer = RelaxedGraphPlan.ActionLayer()
        for action in self.__uncollected_actions:
            action_preconditions = set(action.preconditions)
            if action_preconditions.issubset(self.__initial_state) or not action_preconditions:
                self.__uncollected_actions.remove(action)
                self.__collected_actions.add(action)
                initial_action_layer.add(action)
        self.__action_layers.append(initial_action_layer)


def __expand(self):
    """Make a step forward in the process of building the planning graph, making true that:
        * a in Ax => a not in Ay, for any y > x
    """
    last_action_layer = self.__action_layers[-1]
    next_action_layer = self.ActionLayer(
        {RelaxedGraphPlan.ActionLayer.NoOpAction(prop) for prop in last_action_layer.preconditions}
    )
    for action in self.__uncollected_actions:
        if action.preconditions.issubset(last_action_layer.property_layer):
            self.__uncollected_actions.remove(action)
            self.__collected_actions.add(action)
            next_action_layer.add(action)


def __goal_reached(self):
    """Check if the specified goal state was reached or not.
    :return: None if no goal state was specified, True if the last action layer contains the goal state, False otherwise
    :rtype: bool|None
    """
    return self.__goal_state.issubset(self.__action_layers[-1].property_layer) if self.__goal_state else False


def __solution_possible(self):
    """Check if is it possible to reach the goal state.
    :return: True if goal is already reached or if the graph is expandable, False if fixed point was reached.
    :rtype: bool
    """
    if self.__goal_reached():
        return True
    else:
        # if no goal state was specified or goal is not reached yet, check for possibility to expand the graph
        last_action_layer = self.__action_layers[-1]
        return last_action_layer.preconditions != last_action_layer.property_layer


# def checkpreconditions(preconditions):
# resolvable = list()
# for precondition in preconditions:
#         # check if property value exists into registry
#         # even if no module provide it (e.g. user-given)
#         if WatComponent.precondition(str(precondition)) is not None:
#             if isinstance(precondition, Constraint):
#                 if precondition.compare(WatComponent.precondition(str(precondition))):
#                     continue
#                 else:
#                     return None, False
#             elif isinstance(precondition, Property):
#                 continue
#         else:
#             try:
#                 # Check if python package exists to resolve given precondition
#                 module = importlib.import_module('.'.join([wat.packages.components, str(precondition)]))
#                 # Check if provided module is a WAT module or not,
#                 # if it is, check for submodules entry (there must be at least one)
#                 if not hasattr(module, '__modules__') or not module.__modules__:
#                     return None, False
#             except ImportError:
#                 return None, False
#             resolvable.append(precondition)
#     # ok, all preconditions are resolved/resolvable
#     return resolvable, True