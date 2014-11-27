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

import sys

from wat import conf
from wat.lib.exceptions import InvalidTypeError, WatError, ClientError
from wat.lib.graph import RelaxedGraphPlan
from wat.lib.properties import Property, Registry
from wat.lib.shortcuts import hierlogger as logger

from arguments import parse as parse_arguments
from log import config as logging_config


def banner():
    return r"""
                     __      __    ______    ______
                    /\ \  __/\ \  /\  _  \  /\__  _\
                    \ \ \/\ \ \ \ \ \ \L\ \ \/_/\ \/
                     \ \ \ \ \ \ \ \ \  __ \   \ \ \
                      \ \ \_/ \_\ \ \ \ \/\ \   \ \ \
                       \ `\___x___/  \ \_\ \_\   \ \_\
                        `\/__//__/    \/_/\/_/    \/_/  FRAMEWORK

    WAT Framework  Copyright (C) 2014  Francesco Marano and individual contributors.
    This program comes with ABSOLUTELY NO WARRANTY;
    This is free software, and you are welcome to redistribute it
    under certain conditions; look at doc/LICENSE for details.
    """


def main():
    print banner()
    options = parse_arguments()
    logging_config(colored=options.colored, debugging=options.debugging, level=options.level)

    if hasattr(options, 'search'):
        from wat.lib import search
        if options.search == 'components':
            if options.postcondition is None and options.preconditions is None:
                print "No postcondition and/or preconditions specified. Use --all to show all the components"
                sys.exit()
            components = search.components(options.postcondition, options.preconditions)
            print "Found %d result(s)" % len(components)
            for index, component in enumerate(components, start=1):
                print "%(no.)d.\t%(component)s (r:%(released)s, u:%(updated)s)\n\t\t%(description)s\n" % {
                    'no.': index,
                    'component': component,
                    'released': component.released,
                    'updated': component.updated,
                    'description': component.description,
                }
        elif options.search == 'properties':
            if options.containing is None and options.not_containing is None:
                print "No keywords specified. Use --all to show all the components"
                sys.exit()
            properties = search.properties(options.containing, options.not_containing)
            logger().info("Found %d result(s)" % len(properties))
            for index, prop in enumerate(properties, start=1):
                print "%(no.)d.\t%(property)s" % {
                    'no.': index,
                    'property': prop
                }
        sys.exit()

    clients_conf = conf.clients.instance()
    clients_conf.URL = options.url
    clients_conf.PORT = options.port
    clients_conf.FOLLOWLOCATION = options.followlocation
    if options.proxy is not None:
        clients_conf.PROXY = options.proxy

    # build the planning graph problem
    try:
        rgp = RelaxedGraphPlan(
            initial_state=options.initial_state,
            goal_state=options.goal_state,
            fail_on_invalid=options.fail_on_invalid
        )
    except (InvalidTypeError, WatError) as errors:
        for error in errors:
            logger().critical(error)
        sys.exit(1)

    solution = rgp.solution
    if solution is None:
        print "No solution found"
        sys.exit()
    try:
        solution.execute()
    except ClientError as error:
        for message in error.messages:
            logger().critical(message)
        sys.exit()

    # if goal was specified show only goal state properties
    if rgp.goal_state is not None:
        results = dict(
            (prop, value) for prop, value in Registry.instance().iteritems()
            if Property(prop) in rgp.goal_state
        )
    # if no goal was specified show all retrieved properties
    else:
        results = Registry.instance()
    # print the results
    if results:
        print
        print "Retrieved properties:"
        for index, prop_value in enumerate(results.iteritems(), start=1):
            prop, value = prop_value
            print "\t%d.\t%s:\t%s" % (index, prop, str(value))


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.argv.append('--usage')
    main()