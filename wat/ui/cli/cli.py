# WAT Framework, make simple to do the complex
# Copyright 2014 Francesco Marano and individual contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

import wat
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
           \ `\___x___/  \ \_\ \_\   \ \_\   v%(version)s
            `\/__//__/    \/_/\/_/    \/_/  FRAMEWORK

    """ % {'version': wat.project.version}


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
            print "Found %d result(s)" % len(properties)
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
    if options.host is not None:
        clients_conf.HTTPHEADER.append("Host: %s" % options.host)
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
            logger(depth=1).critical(error)
        sys.exit(1)

    solution = rgp.solution
    if solution is None:
        print "No solution found"
        sys.exit()
    try:
        solution.execute()
    except ClientError as error:
        for message in error.messages:
            logger(depth=1).critical(message)
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
    # remove initial state properties from results
    if options.initial_state:
        initial_properties = [prop_value[0] for prop_value in options.initial_state]
        results = {prop: value for prop, value in results.iteritems() if prop not in initial_properties}
    # print the results
    if results:
        print "\nRetrieved properties:"
        for index, prop_value in enumerate(results.iteritems(), start=1):
            prop, value = prop_value
            print "\t%d.\t%s:\t%s" % (index, prop, str(value))
    else:
        print "\nNo property retrieved"


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.argv.append('--usage')
    main()