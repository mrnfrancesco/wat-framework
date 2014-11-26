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
import logging

from wat.lib import components, search
from wat.lib.components import WatComponent
from wat.lib.exceptions import InvalidTypeError, PropertyNotAchievedError, PropertyDoesNotExist, WatError, \
    InvalidComponentError, ClientError, ComponentFailure
from wat.lib.properties import Property, Registry
from wat.lib.shortcuts import hierlogger as logger


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
                    self.preconditions = {prop}
                    self.postcondition = prop
                else:
                    raise InvalidTypeError(prop, expected=Property)

            def __repr__(self):
                return "NoOpAction('%s')" % str(self.postcondition)

        def __init__(self, actions=None):
            """Initialize an Action Layer from the specified actions which should be all wat components.
            :param actions: the actions to add in the action layer
            :type actions: set|list|tuple
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
                raise InvalidTypeError(actions, (list, set, tuple))

        def __len__(self):
            """Return the number of actions in the action layer"""
            return len(self.actions)

        def add(self, action):
            """Add an action to the current action layer
            :param action: the action to add
            :type action: RelaxedGraphPlan.ActionLayer.NoOpAction|WatComponent
            :raise InvalidTypeError: if the specified action is not a NoOpAction or a WatComponent
            """
            if isinstance(action, RelaxedGraphPlan.ActionLayer.NoOpAction) or components.iswatcomponent(action):
                self.actions.add(action)
            else:
                raise InvalidTypeError(action, (RelaxedGraphPlan.ActionLayer.NoOpAction, WatComponent))

        def remove(self, action):
            """Remove the specified action from the current action layer if it is present in it, otherwise do nothing
            :param action: the action to remove
            """
            self.actions.discard(action)

        @property
        def equivalent_actions(self):
            """Two actions a1 and a2 are equivalent iff postcondition(a1) = postcondition(a2)
            :return: all the actions in the current action layer, grouped by postcondition provided
            :rtype: dict[WatComponent]
            """
            equivalent_actions = dict()
            for action in self.actions:
                postcondition = str(action.postcondition)
                if postcondition in equivalent_actions:
                    equivalent_actions[postcondition].add(action)
                else:
                    equivalent_actions[postcondition] = {action}
            return equivalent_actions

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
            return set(action.postcondition for action in self.actions)

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

        :raise InvalidTypeError: If the initial state or goal state are not of the required type
        :raise WatError: If there is at least an invalid initial state or goal state and *fail_on_invalid* is set to True
        """
        # Check and register initial state

        filtered_initial_state = set()
        if isinstance(initial_state, (list, set, tuple)):
            if all(isinstance(prop_value, tuple) and len(prop_value) == 2 for prop_value in initial_state):
                initial_state_errors = list()
                for prop, value in initial_state:
                    if isinstance(prop, str):
                        WatComponent.register({prop: value})
                        filtered_initial_state.add(Property(prop))
                    else:
                        initial_state_errors.append(InvalidTypeError(prop, (str,)))
                if fail_on_invalid and initial_state_errors:
                    raise WatError(initial_state_errors)
                elif initial_state_errors:
                    for error in initial_state_errors:
                        logger().warning(error)
                self.initial_state = filtered_initial_state
            else:
                raise WatError(message=TypeError('Only pair tuple accepted'), code='invalid')
        elif initial_state is None:
            self.initial_state = set()  # it's ok to have no user-provided properties
        else:
            raise InvalidTypeError(initial_state, (list, set, tuple, type(None)))

        if logger().isEnabledFor(logging.DEBUG):
            logger().info("Initial state is: %s" % [str(prop) for prop in self.initial_state])

        # Check and register goal state
        if isinstance(goal_state, (list, set, tuple)):
            filtered_goal_state = set()
            goal_state_errors = list()
            for prop_name in goal_state:
                if isinstance(prop_name, str):
                    prop = Property(str(prop_name))
                    if prop.exists():
                        filtered_goal_state.add(prop)
                    else:
                        goal_state_errors.extend(PropertyDoesNotExist(prop))
                else:
                    goal_state_errors.extend(InvalidTypeError(prop_name, (str,)))
            if fail_on_invalid and goal_state_errors:
                raise WatError(message=goal_state_errors, code='invalid')
            elif goal_state_errors:
                for error in goal_state_errors:
                    logger().warning(error)
            if filtered_goal_state:
                self.goal_state = filtered_goal_state
            else:
                raise WatError(message='Empty goal state, use None instead', code='failure')
        elif goal_state is None:
            # It means that you want to see what properties you can
            # achieve with the given properties as initial state
            self.goal_state = None
        else:
            raise InvalidTypeError(self.goal_state, (list, set, tuple, type(None)))

        if logger().isEnabledFor(logging.DEBUG):
            if self.goal_state is not None:
                logger().info("Goal state is: %s" % [str(prop) for prop in self.goal_state])
            else:
                logger().info("Undefined goal state, retrieving all possible properties")

        self.__uncollected_actions = set(search.all_components())
        self.__collected_actions = set()  # it collects all the already seen components to avoid loops

        self.action_layers = list()

        # make the first step to build the first action layer
        logger().debug("Expanding graph. Calculating action layer '1'")

        initial_action_layer = RelaxedGraphPlan.ActionLayer()
        for action in self.__uncollected_actions.copy():
            action_preconditions = set(action.preconditions)
            if not action_preconditions or action_preconditions.issubset(self.initial_state):
                self.__uncollected_actions.remove(action)
                self.__collected_actions.add(action)
                initial_action_layer.add(action)
        self.action_layers.append(initial_action_layer)

    def __expand(self):
        """Make a step forward in the process of building the planning graph, making true that:
            * a in Ax => a not in Ay, for any y > x
        """
        if logger().isEnabledFor(logging.DEBUG):
            logger().debug("Expanding graph. Calculating action layer '%d'" % (len(self.action_layers) + 1))

        last_action_layer = self.action_layers[-1]
        next_action_layer = self.ActionLayer(
            {RelaxedGraphPlan.ActionLayer.NoOpAction(prop) for prop in last_action_layer.property_layer}
        )
        for action in self.__uncollected_actions.copy():
            if action.preconditions.issubset(last_action_layer.property_layer):
                self.__uncollected_actions.remove(action)
                self.__collected_actions.add(action)
                next_action_layer.add(action)
        self.action_layers.append(next_action_layer)

    def __goal_reached(self):
        """Check if the specified goal state was reached or not.
        :returns None: if no goal state was specified
        :returns True: if the last action layer contains the goal state
        :returns False: otherwise
        """
        return self.goal_state.issubset(self.action_layers[-1].property_layer) if self.goal_state else None

    def __solution_possible(self):
        """Check if is it possible to reach the goal state.
        :returns True: if goal is already reached or if the graph is expandable
        :returns False: if fixed point was reached without solution
        """
        if self.__goal_reached():
            return True
        else:
            # if no goal state was specified or goal is not reached yet, check for possibility to expand the graph
            last_action_layer = self.action_layers[-1]
            return last_action_layer.preconditions != last_action_layer.property_layer

    @property
    def solution(self):
        class LayeredPlan(object):

            def __init__(self, planning_graph):
                # copy the goal state as property name list
                if planning_graph.goal_state is not None:
                    self.__goal_state = [str(prop) for prop in planning_graph.goal_state]
                else:
                    self.__goal_state = None
                # build the action layers which represent the solution
                self.action_layers = list()
                # copy backwards the graph structure
                for action_layer in planning_graph.action_layers[::-1]:
                    if self.action_layers:  # mantain the actions which need for these properties
                        precondition_needed = self.action_layers[-1].preconditions
                    elif planning_graph.goal_state:  # if first step take them from specified goal state if any
                        precondition_needed = planning_graph.goal_state
                    else:
                        # if no goal was specified mantain all actions as side-effect of
                        # choosing as needed all the precondition in the last action layer
                        precondition_needed = planning_graph.action_layers[-1].preconditions
                    # clean up all the unused actions (those with useless postcondition)
                    for action in action_layer.actions.copy():
                        if action.postcondition not in precondition_needed:
                            action_layer.remove(action)
                    # remove all the NoOpAction and check if some action remain
                    action_layer = RelaxedGraphPlan.ActionLayer(
                        actions=[
                            action for action in action_layer.actions
                            if not isinstance(action, RelaxedGraphPlan.ActionLayer.NoOpAction)
                        ]
                    )
                    if len(action_layer):
                        # copy the remaining action layer at the beginning of the layered plan
                        self.action_layers.insert(0, action_layer)

            def execute(self):
                _logger = logger()
                _logger.info("Executing solution")
                registry = Registry.instance()
                for layer_no, layer in enumerate(self.action_layers, start=1):
                    _logger.debug("Executing action layer '%d'" % layer_no)
                    for prop, actions in layer.equivalent_actions.iteritems():
                        _logger.debug("Retrieving '%s' property" % prop)
                        for component in actions:
                            if prop not in registry:
                                # if the component is not runnable go ahead
                                if not all(str(prop) in registry for prop in component.preconditions):
                                    _logger.debug("Component '%s' is not able to run" % component)
                                    continue
                                try:
                                    _logger.debug("Executing component '%s'" % component)
                                    component().execute()
                                except (InvalidComponentError, ComponentFailure) as error:
                                    _logger.exception("%(code)s: %(message)s" % {
                                        'code': error.code if hasattr(error, 'code') else 'failure',
                                        'message': error.messages
                                    })
                                else:
                                    # if no error raised and property was saved
                                    # go ahead with the next one
                                    if self.__goal_state is None or prop in self.__goal_state:
                                        _logger.info("Goal property '%s' succesfully retrieved" % prop)
                                    else:
                                        _logger.debug("Property '%s' succesfully retrieved" % prop)
                                    break
                        if prop not in registry:
                            _logger.error(PropertyNotAchievedError(prop))
                _logger.info("Execution completed succesfully")

        while True:
            # Termination is granted by fixed-point level.
            # A fixed-point level in a planning graph G is a level k such that for all i > k
            # level i of G is identical to level k.
            goal_reached = self.__goal_reached()
            if goal_reached:
                logger().info("Goal is reachable")
                return LayeredPlan(self)
            else:
                if self.__solution_possible():
                    self.__expand()  # go ahead with the next step
                else:
                    # the graph is no more expandable, but no goal state
                    # was specified, so the solution is all the graph
                    # when fixed-point layer is reached
                    if goal_reached is None:
                        logger().info("Solution set as all reachable properties")
                        return LayeredPlan(self)  # return all as solution
                    else:  # fixed-point level was reached, but goal state was not
                        logger().info("No solution found")
                        return None