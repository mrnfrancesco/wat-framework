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

import os
import pycurl
import importlib
from datetime import date

from it.mrnfrancesco.framework import wat
from it.mrnfrancesco.framework.wat.lib import clients
from it.mrnfrancesco.framework.wat.lib.properties import *
from it.mrnfrancesco.framework.wat.lib.models import Author
from it.mrnfrancesco.framework.wat.lib.exceptions import NotSupportedError, ImproperlyConfigured


def info(authors, released, updated, dependencies=None, version='unknown'):
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
        if not dependencies:  # if None or empty, save as None
            cls.dependencies = None
        elif all(isinstance(spec, (Property, Constraint, Operation)) for spec in dependencies):
            cls.dependencies = dependencies
        else:
            raise AttributeError(
                "dependency type must be one of '%s, %s, %s'" %
                (Property.__name__, Constraint.__name__, Operation.__name__)
            )
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

        # A little hack to add provided property available to every module class
        module = importlib.import_module(cls.__module__)
        filename, _ = os.path.splitext(module.__file__)
        filename = filename.replace(wat.dirs.modules, '')
        filename = filename.rpartition(os.path.sep)[0]
        cls.property_name = filename.replace(os.path.sep, '.')[1:]
        del module

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
                if self.check() is False:
                    raise  # raise error to say 'this module cannot run'
            except NotSupportedError:
                # TODO: add some logging here
                pass  # go ahead and try to run the module

        try:
            provided = self.run()
        except pycurl.error as error:
            raise error  # raise a proper wrapper error

        if hasattr(self, '__provides__'):  # if more values should be provided
            # TODO: check this import (it should NOT works!)
            provides = __import__(self.property_name, fromlist=['__provides__'])
            if isinstance(provided, dict):  # provided properties must be a dict consistent with __provides__

                if set(provided.keys()).isdisjoint(provides):
                    raise ImproperlyConfigured("'__provides__' list and provided properties does not match")

                if len(provided) is not len(provides):
                    if len(provided) > len(provides):
                        raise ImproperlyConfigured(
                            message="only properties in '__provides__' list must be returned, extra %(properties)s",
                            params={'properties': list(set(provided.keys()).difference(provides))}
                        )
                    else:
                        raise ImproperlyConfigured(
                            message="all properties in '__provides__' list must be returned, missing %(properties)s",
                            params={'properties': list(set(provides).difference(provided.keys()))}
                        )

        # 'provided' seems good. Let's save them!
        Registry.instance()[self.property_name] = provided

        return self

    def __exit__(self):
        self.curl.close()

    # Some useful functions to avoid module developer to know about some hack
    @staticmethod
    def provide(prop, value):
        if prop not in Registry.instance():
            Registry.instance()[prop] = value

    getdependency = staticmethod(lambda prop: Registry.instance()[prop] if prop in Registry.instance() else None)
    save_as_attribute = lambda self, name: lambda value: self.__setattr__(name, value)