import unittest
from wat.lib.exceptions import InvalidTypeError
from wat.lib.graph import RelaxedGraphPlan
from wat.lib.properties import Property, Constraint


class NoOpActionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.property_name = 'website.cms.opencart.version'
        cls.property_obj = Property(cls.property_name)
        cls.constraint_obj = Constraint(cls.property_name, expected=None)

    def test_init(self):
        # property parameter must be of type Property or subclasses
        self.assertRaises(
            excClass=InvalidTypeError,
            callableObj=RelaxedGraphPlan.ActionLayer.NoOpAction,
            prop='an invalid type'
        )
        # Property and Constraint type is ok
        RelaxedGraphPlan.ActionLayer.NoOpAction(self.property_obj),
        RelaxedGraphPlan.ActionLayer.NoOpAction(self.constraint_obj),

    def test_preconditions(self):
        self.assertSetEqual(
            {self.property_obj},
            RelaxedGraphPlan.ActionLayer.NoOpAction(self.property_obj).preconditions
        )

    def test_postcondition(self):
        self.assertEqual(
            self.property_obj,
            RelaxedGraphPlan.ActionLayer.NoOpAction(self.property_obj).postcondition
        )


class ActionLayerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from wat.components.website.cms.opencart.version.footer import GetVersionByFooter
        cls.action = GetVersionByFooter

    def test_init(self):
        # actions parameter must be of type list, set or tuple
        self.assertRaises(
            excClass=InvalidTypeError,
            callableObj=RelaxedGraphPlan.ActionLayer,
            actions='an invalid type'
        )
        # list, set and tuple and None types are ok
        RelaxedGraphPlan.ActionLayer()
        RelaxedGraphPlan.ActionLayer(actions=[self.action])
        RelaxedGraphPlan.ActionLayer(actions={self.action})
        RelaxedGraphPlan.ActionLayer(actions=(self.action,))

    def test_len(self):
        self.assertEqual(1, len(RelaxedGraphPlan.ActionLayer(actions={self.action})))

    def test_add(self):
        layer = RelaxedGraphPlan.ActionLayer()
        self.assertSetEqual(set(), layer.actions)
        # adding a valid wat component as action
        layer.add(self.action)
        self.assertSetEqual({self.action}, layer.actions)
        # adding again the same action should provide no changes
        layer.add(self.action)
        self.assertSetEqual({self.action}, layer.actions)
        # action parameter must bu a valid wat component
        self.assertRaises(
            excClass=Exception,
            callableObj=layer.add,
            action='an invalid type'
        )

    def test_remove(self):
        layer = RelaxedGraphPlan.ActionLayer(actions={self.action})
        # it wont do anything
        layer.remove('not an action')
        self.assertSetEqual({self.action}, layer.actions)
        # it will remove the action from the action layer
        layer.remove(self.action)
        self.assertSetEqual(set(), layer.actions)

    def test_preconditions(self):
        # no actions means no preconditions
        self.assertSetEqual(set(), RelaxedGraphPlan.ActionLayer().preconditions)
        # one action means its preconditions
        self.assertSetEqual(
            self.action.preconditions,
            RelaxedGraphPlan.ActionLayer(actions={self.action}).preconditions
        )

    def test_postconditions(self):
        # no actions means no postconditions
        self.assertSetEqual(set(), RelaxedGraphPlan.ActionLayer().postconditions)
        # one action means its postcondition
        self.assertSetEqual(
            {Property(self.action.postcondition)},
            RelaxedGraphPlan.ActionLayer(actions={self.action}).postconditions
        )

    def test_property_layer(self):
        # no actions means no property layer
        self.assertSetEqual(set(), RelaxedGraphPlan.ActionLayer().property_layer)
        # one action means its preconditions and its postcondition
        self.assertSetEqual(
            self.action.preconditions.union({Property(self.action.postcondition)}),
            RelaxedGraphPlan.ActionLayer(actions={self.action}).property_layer
        )


class RelaxedGraphPlanTestCase(unittest.TestCase):
    pass  # TODO!