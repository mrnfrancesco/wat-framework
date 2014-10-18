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

__all__ = ['project', 'author', 'dirs', 'files']

from os.path import join, dirname


class project(object):
    name = "WAT Framework"
    version = "0.0.1"
    description = None
    links = {
        'sources': "https://bitbucket.org/mrnfrancesco/wat-framework",
        'issues': "https://bitbucket.org/mrnfrancesco/wat-framework/issues",
        'wiki': "https://bitbucket.org/mrnfrancesco/wat-framework/wiki",
        'doc': None,
    }


class author(object):
    name = "Francesco Marano"
    nickname = "mrnfrancesco"
    references = {
        'email': "francesco.mrn24@gmail.com",
        'github': "https://github.com/mrnfrancesco",
        'twitter': "http://twitter.com/mrnfrancesco",
        'linkedin': "http://it.linkedin.com/in/mrnfrancesco",
    }


class dirs(object):

    __slots__ = {'install', 'lib', 'modules', 'data', 'doc'}

    install = dirname(dirname(__file__))
    lib = join(install, 'lib')
    modules = join(install, 'modules')
    data = join(install, 'data')
    doc = join(install, 'doc')


class files(object):

    __slots__ = {'database', 'useragents'}

    database = join(dirs.modules, 'wat.db')
    useragents = join(dirs.data, 'user-agents.lst')