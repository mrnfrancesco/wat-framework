# WAT Framework, make simple to do the complex
# Copyright 2014 Francesco Marano and individual contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = {'parse'}

import argparse
from textwrap import dedent as _

import wat


class _NoArgsAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
        super(_NoArgsAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help
        )

class _UsageAction(_NoArgsAction):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_usage()
        parser.exit()


class _RandomUserAgentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        with open(name=wat.files.useragents, mode='r') as f:
            from random import randint

            user_agents = f.readlines()
            setattr(namespace, self.dest, user_agents[randint(0, len(user_agents) - 1)])


class _UrlAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        if value[-1] is not '/':
            value = "%s/" % value
        setattr(namespace, self.dest, value)


class _ShowAllPropertiesAction(_NoArgsAction):
    def __call__(self, parser, namespace, value, option_string=None):
        from wat.lib import search

        properties = search.properties()
        print "Found %d result(s)" % len(properties)
        for index, prop in enumerate(properties, start=1):
            print "%(no.)d.\t%(property)s" % {
                'no.': index,
                'property': str(prop)
            }
        parser.exit()


class _ShowAllComponentsAction(_NoArgsAction):
    def __call__(self, parser, namespace, value, option_string=None):
        from wat.lib import search

        components = search.components()
        print "Found %d result(s)" % len(components)
        for index, component in enumerate(search.components(), start=1):
            print "%(no.)d.\t%(component)s (r:%(released)s, u:%(updated)s)\n\t\t%(description)s\n" % {
                'no.': index,
                'component': component,
                'released': component.released,
                'updated': component.updated,
                'description': component.description,
            }
        parser.exit()


def parse(arguments=None):
    # Initialize the parser object
    parser = argparse.ArgumentParser(prog='watf', add_help=False, fromfile_prefix_chars="@")
    # create a subparser object
    subparsers = parser.add_subparsers()

    # Output
    parser.add_argument('--help', help="show this help message and exit", action="help")
    parser.add_argument('--usage', help="show the usage and exit", action=_UsageAction)
    parser.add_argument('--version', help="show the framework version an exit", action="version",
                        version="%s %s" % (wat.project.name, wat.project.version))
    output = parser.add_argument_group('Output')
    output.add_argument('-d', '--debugging', default=False, action="store_true",
                        help="set output format to a more verbose one, for debugging purpose (default: %(default)s)")
    output.add_argument('-l', '--level', help="set output verbosity (default: %(default)s)",
                        choices=['debug', 'info', 'warning', 'error', 'critical'], default='info')
    # Output > Color
    color = output.add_mutually_exclusive_group(required=False)
    color.add_argument('-c', '--color', dest="colored", help="use color in the output", action="store_true",
                       default=True)
    color.add_argument('-nc', '--no-color', dest="colored", help="do not use color in the output",
                       action="store_false")

    # Search
    search_parser = subparsers.add_parser('search', add_help=False,
                                          help="search functionalities for components and properties")
    search_parser.add_argument('--help', help="show this help message and exit", action="help")
    search_parser.add_argument('--usage', help="show the usage and exit", action=_UsageAction)
    search_subparsers = search_parser.add_subparsers(dest="search")
    # Search > Components
    search_components_parser = search_subparsers.add_parser('components', add_help=False, help="search for components")
    search_components_parser.add_argument('-a', '--all', action=_ShowAllComponentsAction,
                                         help="show all the components and exit")
    search_components_parser.add_argument('-post', '--postcondition', metavar="PROPERTY",
                                         help="the property all the components must have as postcondition")
    search_components_parser.add_argument('-pre', '--preconditions', metavar="PROPERTY", nargs="+",
                                         help="the properties all the components must have as preconditions")
    search_components_parser.add_argument('--help', help="show this help message and exit", action="help")
    search_components_parser.add_argument('--usage', help="show the usage and exit", action=_UsageAction)
    # Search > Properties
    search_properties_parser = search_subparsers.add_parser('properties', add_help=False, help="search for properties")
    search_properties_parser.add_argument('-a', '--all', action=_ShowAllPropertiesAction,
                                          help="show all the properties and exit")
    search_properties_parser.add_argument('-c', '--containing', metavar="KEYWORD", nargs="+",
                                          help="the keywords all the properties must have in their name")
    search_properties_parser.add_argument('-nc', '--not-containing', metavar="KEYWORD", nargs="+",
                                          help="the keywords all the properties must not have in their name")
    search_properties_parser.add_argument('--help', help="show this help message and exit", action="help")
    search_properties_parser.add_argument('--usage', help="show the usage and exit", action=_UsageAction)

    # Run
    run_parser = subparsers.add_parser(
        'run',
        add_help=False,
        help="run the framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_("""
                Examples:
                    - Tell everything possible about "http://foo.bar.com/", without initial information:
                        %(prog)s --url foo.bar.com
            """)
    )
    # Run > Framework
    framework = run_parser.add_argument_group('Framework')
    framework.add_argument('-i', '--init', dest="initial_state", nargs=2, metavar=('PROPERTY', 'VALUE'),
                           help="add PROPERTY=VALUE in the initial state", action="append")
    framework.add_argument('-g', '--goal', dest="goal_state", metavar="PROPERTY",
                           help="add PROPERTY in the goal state", action="append")
    fail = framework.add_mutually_exclusive_group(required=False)
    fail.add_argument('-f', '--fail', dest="fail_on_invalid", action="store_true")
    fail.add_argument('-nf', '--no-fail', dest="fail_on_invalid", action="store_false", default=False)

    # Run > Network
    network = run_parser.add_argument_group('Network')
    network.add_argument('-u', '--url', required=True, help="the target URL", action=_UrlAction)
    network.add_argument('-h', '--host', help="use the specified host (in case of virtual hosts)")
    network.add_argument('-p', '--port', help="use the specified port", type=int, default=80)
    # Run > Network > Proxy
    proxy = network.add_mutually_exclusive_group(required=False)
    proxy.add_argument('--no-proxy', action="store_const", dest="proxy", const="",
                       help="no proxy, environmental one will be ignored")
    # Run > Network > Proxy > Custom Proxy
    # TODO: add proxy username and password support
    # FIXME: check proxy help for real supported protocol
    proxy.add_argument('--proxy', metavar="SCHEME://(HOSTNAME|IP):PORT", dest="proxy",
                       help="supply a proxy. HTTP, SOCKS4 SOCKS4A and SOCKS5 are supported.")
    # Run > Network > User-Agent
    user_agent = network.add_mutually_exclusive_group(required=False)
    user_agent.add_argument('-a', '--user-agent', dest="user_agent", metavar="USER-AGENT",
                            help="use the specified User-Agent")
    user_agent.add_argument('-ra', '--random-user-agent', nargs=0, dest="user_agent", metavar="USER-AGENT",
                            help="use a random User-Agent", action=_RandomUserAgentAction)
    # Run > Network > Redirection
    redirection = network.add_mutually_exclusive_group(required=False)
    redirection.add_argument('-3xx', '--follow-redirection', dest="followlocation",
                             help="if the target url has a redirection, it will be followed", action="store_true")
    redirection.add_argument('-no-3xx', '--no-redirection', dest="followlocation", default=False,
                             help="if the target url has a redirection, it will not be followed", action="store_false")
    # Run > Info
    info = run_parser.add_argument_group('Info')
    info.add_argument('--help', help="show this help message and exit", action="help")
    info.add_argument('--usage', help="show the usage and exit", action=_UsageAction)

    return parser.parse_args(arguments)