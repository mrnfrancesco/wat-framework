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
import wat

__all__ = ['info', 'MetaComponent', 'WatComponent']

import os
import pycurl
import importlib
from datetime import date

from wat.lib import clients
from wat.lib.properties import *
from wat.lib.models import Author
from wat.lib.exceptions import ImproperlyConfigured, InvalidTypeError


def info(authors, released, updated, preconditions=None, version='unknown'):
    def wrap(cls):
        # write all the info parameters into class definition looking for misconfiguration
        if all(isinstance(author, Author) for author in authors):
            cls.authors = authors
        else:
            raise InvalidTypeError('authors', Author)
        if isinstance(released, date):
            cls.released = released
        if isinstance(updated, date):
            cls.updated = updated
        if not preconditions:  # if None or empty, save as empty
            cls.preconditions = set()
        elif all(isinstance(spec, (Property, Constraint)) for spec in preconditions):
            cls.preconditions = set(preconditions)
        else:
            raise InvalidTypeError('preconditions', Property)
        # save the version as string, whatever type it really is
        cls.version = str(version)

        return cls

    return wrap


class MetaComponent(type):
    def __init__(cls, name, bases, attr):
        super(MetaComponent, cls).__init__(name, bases, attr)
        cls.name = name
        if cls.__doc__:
            cls.description = cls.__doc__
        else:
            raise AttributeError("missing description")

        # A little hack to add provided property available to every module class
        module = importlib.import_module(cls.__module__)
        filename, _ = os.path.splitext(module.__file__)
        filename = filename.replace(wat.dirs.components, '')
        filename = filename.rpartition(os.path.sep)[0]
        cls.postcondition = filename.replace(os.path.sep, '.')[1:]

    def run(self):
        """Use the preconditions to provide the postcondition.
        :return: the postcondition gained
        :raise NotImplementedError: if run method was not implemented
        """
        raise NotImplementedError


class WatComponent(object):
    def __enter__(self):
        try:
            provided = self.run()
        except pycurl.error as error:
            raise error  # raise a proper wrapper error

        if hasattr(self, '__provides__'):  # if more values should be provided
            provides = __import__('.'.join([wat.packages.components, self.postcondition])).__provides__
            if isinstance(provided, dict):  # provided postconditions must be a dict consistent with __provides__

                if set(provided.keys()).isdisjoint(provides):
                    raise ImproperlyConfigured("'__provides__' list and provided properties does not match")

                if len(provided) is not len(provides):
                    if len(provided) > len(provides):
                        raise ImproperlyConfigured(
                            message="only properties in '__provides__' list must be returned, extra '%(properties)s'",
                            params={'properties': list(set(provided.keys()).difference(provides))}
                        )
                    else:
                        raise ImproperlyConfigured(
                            message="all properties in '__provides__' list must be returned, missing '%(properties)s'",
                            params={'properties': list(set(provides).difference(provided.keys()))}
                        )
            else:
                raise  # TODO: raise exception to say "return type must be dict"

        # 'provided' seems good. Let's save them!
        Registry.instance()[self.postcondition] = provided

        return self

    @staticmethod
    def precondition(prop):
        registry = Registry.instance()
        return registry[prop] if prop in registry else None

    @staticmethod
    def register(prop_value):
        """Register the specified property with the given value if it is not already
        present into the preconditions registry.

        All the <property,value> pairs MUST be in the form of:
         - dict, `WatComponent.register({'prop': value,})`
         - list, `WatComponent.register([(prop, value),])`
         - set, `WatComponent.register({(prop, value),})`

        :param prop_value: all the <property,value> pairs to register
        """
        registry = Registry.instance()

        def _register(key, val):
            if key not in registry:
                registry[key] = val

        if isinstance(prop_value, dict):
            for prop in prop_value:
                _register(prop, prop_value[prop])
        else:
            for prop, value in prop_value:
                _register(prop, value)

    save_as_attribute = lambda self, name: lambda value: self.__setattr__(name, value)


def iswatcomponent(cls):
    """
    :param cls: the class you want to know if it is a Wat component
    :type cls: class
    :rtype: bool
    :return: `True` if the specified class is a Wat component, `False` otherwise
    """
    return WatComponent in cls.__bases__ and isinstance(cls, MetaComponent)


def module_from(path):
    """
    Return the dotted notation name of a module from its path.
     Note that the returned string is ready to be imported.
    :param path: the absolute path of the module you want to convert
    :return: the module package and name in dotted notation
    """
    return path.replace(wat.dirs.install, '').replace(os.path.sep, '.')[1:]