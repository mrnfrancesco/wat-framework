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

__all__ = ['project', 'author', 'dirs', 'files', 'packages']

from os.path import join, dirname


class project(object):

    __slots__ = {'name', 'version', 'description', 'links'}

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

    __slots__ = {'name', 'nickname', 'references'}

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

    install = dirname(__file__)
    lib = join(install, 'lib')
    modules = join(install, 'modules')
    data = join(install, 'data')
    doc = join(install, 'doc')


class files(object):

    __slots__ = {'useragents'}

    useragents = join(dirs.data, 'user-agents.lst')


class docs(object):

    __slots__ = {
        'agreement', 'changelog', 'contribute', 'contributors',
        'credits', 'disclaimer', 'faq', 'license', 'readme', 'thanks'
    }

    agreement = join(dirs.doc, 'AGREEMENT')
    changelog = join(dirs.doc, 'CHANGELOG')
    contribute = join(dirs.doc, 'CONTRIBUTE')
    contributors = join(dirs.doc, 'CONTRIBUTORS')
    credits = join(dirs.doc, 'CREDITS')
    disclaimer = join(dirs.doc, 'DISCLAIMER')
    faq = join(dirs.doc, 'FAQ')
    license = join(dirs.doc, 'LICENSE')
    readme = join(dirs.doc, 'README')
    thanks = join(dirs.doc, 'THANKS')


class packages(object):

    __slots__ = {'base', 'modules'}

    base = __name__  # it stands for "it.mrnfrancesco.framework.wat"
    modules = '.'.join([base, 'modules'])

