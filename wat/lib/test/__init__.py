import unittest

from wat.lib.test import graph
from wat.lib.test import properties


def suite(testcase, tests):
    return unittest.TestSuite(map(testcase, tests))


def graph_suite():
    return unittest.TestSuite([
        suite(
            testcase=graph.NoOpActionTestCase,
            tests=['test_init', 'test_preconditions', 'test_postcondition']
        ),
        suite(
            testcase=graph.ActionLayerTestCase,
            tests=[
                'test_init', 'test_len', 'test_add', 'test_remove',
                'test_preconditions', 'test_postconditions', 'test_property_layer'
            ]
        ),
    ])


def properties_suite():
    return unittest.TestSuite([
        suite(
            testcase=properties.RegistryTestCase,
            tests=['test_singleton']
        ),
        suite(
            testcase=properties.PropertyTestCase,
            tests=[
                'test_init', 'test_exists', 'test_repr', 'test_eq',
                'test_neq', 'test_hash', 'test_str',
            ]
        ),
        suite(
            testcase=properties.ConstraintTestCase,
            tests=['test_init', 'test_compare', 'test_repr', 'test_eq', 'test_neq']
        ),
    ])


if __name__ == '__main__':
    def run_suite(tests_or_suite):
        return unittest.TextTestRunner(verbosity=2).run(tests_or_suite)

    run_suite(graph_suite())
    run_suite(properties_suite())