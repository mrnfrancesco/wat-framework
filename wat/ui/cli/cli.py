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

from wat import conf
from wat.lib.graph import RelaxedGraphPlan
from wat.lib.properties import Property, Registry


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

    # set a target
    conf.clients.instance().URL = 'http://demo.opencart.com'
    # build the planning graph problem
    rgp = RelaxedGraphPlan(
        initial_state=[
            ('website.cms.name', 'opencart'),
        ],
        fail_on_invalid=True
    )
    # find and execute a solution
    rgp.solution.execute()

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
        print "\n\033[33m[Retrieved properties]\033[0m"
        for prop, value in results.iteritems():
            print "\033[35m%s\033[0m: %s" % (prop, str(value))


if __name__ == '__main__':
    main()