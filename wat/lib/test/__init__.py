import unittest

from wat.lib.test import graph


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


if __name__ == '__main__':
    def run_suite(tests_or_suite):
        return unittest.TextTestRunner(verbosity=2).run(tests_or_suite)

    run_suite(graph_suite())