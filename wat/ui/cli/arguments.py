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

__all__ = {'parse'}

import argparse
from textwrap import dedent as _

import wat


class _UsageAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
        super(_UsageAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help
        )

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


def parse(arguments=None):
    # Initialize the parser object
    parser = argparse.ArgumentParser(
        add_help=False,
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_("""
            Examples:
                - Tell everything possible about "http://foo.bar.com/", without initial information:
                    %(prog)s --url foo.bar.com

                - Load option.args content as arguments:
                    %(prog)s @option.args
        """)
    )

    # Framework
    framework = parser.add_argument_group('Parser')
    framework.add_argument('-i', '--init', dest="initial_state", nargs=2, metavar=('PROPERTY', 'VALUE'),
                           help="add PROPERTY=VALUE in the initial state", action="append")
    framework.add_argument('-g', '--goal', dest="goal_state", metavar="PROPERTY",
                           help="add PROPERTY in the goal state", action="append")

    # Network
    network = parser.add_argument_group('Network')
    network.add_argument('-u', '--url', required=True, help="the target URL", action=_UrlAction)
    network.add_argument('-h', '--host', help="use the specified host (in case of virtual hosts)")
    network.add_argument('-p', '--port', help="use the specified port", type=int, default=80)
    # Network > Proxy
    proxy = network.add_mutually_exclusive_group(required=False)
    proxy.add_argument('--no-proxy', action="store_const", dest="proxy", const="",
                       help="no proxy, environmental one will be ignored")
    # Network > Proxy > Custom Proxy
    # TODO: add proxy username and password support
    # FIXME: check proxy help for real supported protocol
    proxy.add_argument('--proxy', metavar="SCHEME://(HOSTNAME|IP):PORT", dest="proxy",
                       help="supply a proxy. HTTP, SOCKS4 SOCKS4A and SOCKS5 are supported.")
    # Network > User-Agent
    user_agent = network.add_mutually_exclusive_group(required=False)
    user_agent.add_argument('-a', '--user-agent', dest="user_agent", metavar="USER-AGENT",
                            help="use the specified User-Agent")
    user_agent.add_argument('-ra', '--random-user-agent', nargs=0, dest="user_agent", metavar="USER-AGENT",
                            help="use a random User-Agent", action=_RandomUserAgentAction)
    # Network > Redirection
    redirection = network.add_mutually_exclusive_group(required=False)
    redirection.add_argument('-3xx', '--follow-redirection', dest="followlocation",
                             help="if the target url has a redirection, it will be followed", action="store_true")
    redirection.add_argument('-no-3xx', '--no-redirection', dest="followlocation", default=False,
                             help="if the target url has a redirection, it will not be followed", action="store_false")
    # Output
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
    # Info
    info = parser.add_argument_group('Info')
    info.add_argument('--help', help="show this help message and exit", action="help")
    info.add_argument('--version', help="show the framework version an exit", action="version",
                      version="%s %s".format(wat.project.name, wat.project.version))
    info.add_argument('--usage', help="show the usage and exit", action=_UsageAction)

    return parser.parse_args(arguments)