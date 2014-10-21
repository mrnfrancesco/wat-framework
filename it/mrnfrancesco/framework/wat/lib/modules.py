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

__all__ = ['info', 'MetaModule', 'WatModule']

from datetime import date

from it.mrnfrancesco.framework.wat.lib.models import Author
from it.mrnfrancesco.framework.wat.lib.properties import Property, Constraint, Operation, Registry
from it.mrnfrancesco.framework.wat.lib.exceptions import NotSupportedError, ImproperlyConfigured
from it.mrnfrancesco.framework.wat.lib import clients


def info(authors, released, updated, provides, dependencies=None, version='unknown'):
    def wrap(cls):
        # write all the info parameters into class definition looking for misconfiguration
        if all(isinstance(author, Author) for author in authors):
            cls.authors = authors
        else:
            raise AttributeError("all authors must be of type '%s'" % Author.__name__)
        if isinstance(released, date):
            cls.released = released
        if isinstance(updated, date):
            cls.updated = updated
        if provides:  # check for at least one element
            if all(isinstance(spec, str) for spec in provides):
                cls.provides = provides
        if not dependencies:  # if None or empty, save as None
            cls.dependencies = None
        elif all(isinstance(spec, (Property, Constraint, Operation)) for spec in dependencies):
            cls.dependencies = dependencies
        # save the version as string, whatever type it really is
        cls.version = str(version)

        return cls
    return wrap


class MetaModule(type):

    def __init__(cls, name, bases, attr):
        super(MetaModule, cls).__init__(name, bases, attr)
        cls.name = name
        if cls.__doc__:
            cls.description = cls.__doc__
        else:
            raise AttributeError("missing description")
        cls.__checkable__ = hasattr(cls, 'check')

    def check(self):
        """Check if the module is able to run properly.

        :return: `True` if the module is able to run properly, `False` otherwise
        :rtype: bool
        :raise NotImplementedError: if check method was not implemented
        :raise NotSupportedError: if :method:`self.check()` is not supported for this module
        """
        raise NotImplementedError

    def run(self):
        raise NotImplementedError


class WatModule(object):

    def __init__(self):
        self.curl = clients.Curl()
        self.setopt = self.curl.setopt

    def __enter__(self):
        if self.__checkable__:
            try:
                self.check()
            except NotSupportedError:
                # TODO: add some logging here
                pass  # go ahead and try to run the module

        provided = self.run()
        if not isinstance(provided, dict):
            raise ImproperlyConfigured(
                message="run method must return a dict, got %(ret_type)s instead",
                params={'ret_type': type(provided)}
            )

        if set(provided.keys()).isdisjoint(self.provides):
            raise ImproperlyConfigured("'provides' list and provided properties does not match")

        if len(provided) is not len(self.provides):
            if len(provided) > len(self.provides):
                raise ImproperlyConfigured(
                    message="all provided properties must be made explicit, some missing (%(missing)s)",
                    params={'missing': list(set(provided.keys()).difference(self.provides))}
                )
            else:
                raise ImproperlyConfigured(
                    message="all properties in 'provides' list must be given, some missing (%(missing)s)",
                    params={'missing': list(set(self.provides).difference(provided.keys()))}
                )

        # TODO list for saving retrieved properties:
        # 1. get module package, module name and properties name
        # 2. concatenate those strings
        # 3. save values in Registry.instance() dictionary

        return self

    def __exit__(self, exc_type, value, traceback):
        self.curl.close()

# TODO: add :method:verify()