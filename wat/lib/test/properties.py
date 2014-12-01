import unittest
from wat.lib.exceptions import InvalidTypeError
from wat.lib.properties import Registry, Property, Constraint


class RegistryTestCase(unittest.TestCase):
    def test_singleton(self):
        self.assertEqual(Registry.instance(), Registry.instance())


class PropertyTestCase(unittest.TestCase):
    def test_init(self):
        self.assertRaises(
            excClass=InvalidTypeError,
            callableObj=Property,
            name=1234567890  # name should be a string
        )

        Property(name='this.is.a.valid.name')

    def test_exists(self):
        self.assertFalse(Property(name='this.not.exists').exists())
        self.assertTrue(Property(name='website.cms.name').exists())

    def test_repr(self):
        self.assertEqual(Property(name="whatever").__repr__(), "Property('whatever')")

    def test_eq(self):
        prop = Property("whatever")
        self.assertTrue(prop == Property(name="whatever"))
        self.assertFalse(prop == Property(name="something else"))
        self.assertFalse(prop == "whatever")

    def test_neq(self):
        prop = Property("whatever")
        self.assertFalse(prop != Property(name="whatever"))
        self.assertTrue(prop != Property(name="something else"))
        self.assertTrue(prop != "whatever")

    def test_hash(self):
        self.assertEqual(Property(name="whatever").__hash__(), Property(name="whatever").__hash__())
        self.assertNotEqual(Property(name="whatever").__hash__(), Property(name="something else").__hash__())

    def test_str(self):
        self.assertEqual(Property(name="whatever").__str__(), "whatever")


class ConstraintTestCase(unittest.TestCase):
    def test_init(self):
        self.assertRaises(
            excClass=InvalidTypeError,
            callableObj=Constraint,
            name=1234567890,  # name should be a string
            expected='whatever',
            compare_fn='eq'
        )

        Constraint(name='this.is.a.valid.name', expected='whatever', compare_fn='eq')

    def test_compare(self):
        registry = Registry.instance()
        registry['a.valid.property'] = 'foo'
        self.assertTrue(Constraint('a.valid.property', 'foo').compare())
        self.assertTrue(Constraint('a.valid.property', 'foo', 'eq').compare())

        registry['a.valid.property'] = 'bar'
        self.assertFalse(Constraint('a.valid.property', 'foo').compare())
        self.assertFalse(Constraint('a.valid.property', 'foo', 'eq').compare())

        registry['a.valid.property'] = 'aaa'
        self.assertTrue(Constraint('a.valid.property', 'bbb', 'lt').compare())
        self.assertFalse(Constraint('a.valid.property', 'bbb', 'gt').compare())

    def test_repr(self):
        self.assertEqual(Constraint('whatever', 'foo').__repr__(), "Constraint('whatever', 'foo', 'eq')")
        self.assertEqual(Constraint('whatever', 'foo', 'eq').__repr__(), "Constraint('whatever', 'foo', 'eq')")
        self.assertEqual(Constraint('whatever', 'foo', 'bar').__repr__(), "Constraint('whatever', 'foo', 'bar')")

    def test_eq(self):
        prop = Constraint('whatever', 'foo', 'eq')

        self.assertTrue(prop == Property(name='whatever'))
        self.assertFalse(prop == Property(name="something else"))
        self.assertFalse(prop == "whatever")

        self.assertFalse(prop == Constraint('something else', 'foo', 'eq'))
        self.assertFalse(prop == Constraint('whatever', 'bar', 'eq'))
        self.assertFalse(prop == Constraint('whatever', 'foo', 'lt'))

    def test_neq(self):
        prop = Constraint('whatever', 'foo', 'eq')

        self.assertFalse(prop != Property(name='whatever'))
        self.assertTrue(prop != Property(name="something else"))
        self.assertTrue(prop != "whatever")

        self.assertTrue(prop != Constraint('something else', 'foo', 'eq'))
        self.assertTrue(prop != Constraint('whatever', 'bar', 'eq'))
        self.assertTrue(prop != Constraint('whatever', 'foo', 'lt'))