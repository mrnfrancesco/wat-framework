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

    __slots__ = {'install', 'lib', 'components', 'data', 'doc'}

    install = dirname(dirname(__file__))
    base = dirname(__file__)
    lib = join(base, 'lib')
    components = join(base, 'components')
    data = join(base, 'data')
    doc = join(base, 'doc')


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

    __slots__ = {'base', 'components'}

    base = __name__  # it stands for "it.mrnfrancesco.framework.wat"
    components = '.'.join([base, 'components'])

