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

import wat

__all__ = ['info', 'MetaComponent', 'WatComponent']

import os
import pycurl
import importlib
from datetime import date

from wat.lib.properties import *
from wat.lib.models import Author
from wat.lib.exceptions import InvalidTypeError, ClientError, InvalidComponentError, \
    ConstraintViolationError, ComponentFailure


def info(authors, released, updated, preconditions=None, version='unknown'):
    def wrap(cls):
        # write all the info parameters into class definition looking for misconfiguration
        if all(isinstance(author, Author) for author in authors):
            cls.authors = authors
        else:
            raise InvalidTypeError(authors, Author)
        if isinstance(released, date):
            cls.released = released
        if isinstance(updated, date):
            cls.updated = updated
        if not preconditions:  # if None or empty, save as empty
            cls.preconditions = set()
        elif all(isinstance(spec, (Property, Constraint)) for spec in preconditions):
            cls.preconditions = set(preconditions)
        else:
            raise InvalidTypeError(preconditions, Property)
        # save the version as string, whatever type it really is
        cls.version = str(version)

        return cls

    return wrap


class MetaComponent(type):
    def __init__(cls, name, bases, attr):
        super(MetaComponent, cls).__init__(name, bases, attr)
        cls.name = name
        if not cls.__doc__:
            raise InvalidComponentError("missing component description")

        # A little hack to add provided property available to every module class
        module = importlib.import_module(cls.__module__)
        filename, _ = os.path.splitext(module.__file__)
        filename = filename.replace(wat.dirs.components, '')
        filename = filename.rpartition(os.path.sep)[0]
        cls.postcondition = Property(filename.replace(os.path.sep, '.')[1:])

    @property
    def description(cls):
        return cls.__doc__

    def __str__(self):
        return '.'.join([str(self.postcondition), self.name])

    def run(self):
        """Use the preconditions to provide the postcondition.
        :return: the postcondition gained
        :raise NotImplementedError: if run method was not implemented
        """
        raise NotImplementedError


class WatComponent(object):
    def execute(self):
        """Execute the component and register the provided property.

        :raise InvalidComponentError: if *__provides__* was specified, but the component returns does not match it or is not a dict
        :raise ClientError: if some pycurl.error occurred during component running
        :raise ComponentFailure: if component somehow fails
        """
        constraints = [
            constraint for constraint in self.preconditions
            if isinstance(constraint, Constraint)
        ]
        if constraints:
            violations = [
                ConstraintViolationError(constraint) for constraint in constraints
                if constraint.compare() is False
            ]
            if violations:
                raise ComponentFailure(message=violations)

        try:
            provided = self.run()
        except pycurl.error as e:
            raise ClientError(pycurl_error=e)

        if provided is None:
            raise ComponentFailure("Component has returned no value")

        module = importlib.import_module('.'.join([wat.packages.components, str(self.postcondition)]))
        if hasattr(module, '__provides__'):  # if more values should be provided
            provides = module.__provides__
            if isinstance(provided, dict):  # provided postconditions must be a dict consistent with __provides__

                if set(provided.keys()).isdisjoint(provides):
                    raise InvalidComponentError("'__provides__' list and provided properties does not match")

                if len(provided) is not len(provides):
                    if len(provided) > len(provides):
                        raise InvalidComponentError(
                            message="only properties in '__provides__' list must be returned, extra '%(properties)s'",
                            params={'properties': list(set(provided.keys()).difference(provides))}
                        )
                    else:
                        raise InvalidComponentError(
                            message="all properties in '__provides__' list must be returned, missing '%(properties)s'",
                            params={'properties': list(set(provides).difference(provided.keys()))}
                        )
            else:
                raise InvalidComponentError(
                    message=InvalidTypeError(provided, (dict,))
                )

        # 'provided' seems good. Let's save them!
        WatComponent.register([(str(self.postcondition), provided)])

    @staticmethod
    def precondition(prop):
        registry = Registry.instance()
        return registry[prop] if prop in registry else None

    @staticmethod
    def register(prop_value):
        """Register the specified property with the given value if it is not already
        present into the preconditions registry.

        All the <property,value> pairs MUST be in the form of:
         - dict,  `WatComponent.register({'prop': value,})`
         - list,  `WatComponent.register([(prop, value),])`
         - set,   `WatComponent.register({(prop, value),})`

        :param prop_value: all the <property,value> pairs to register
        :type prop_value: dict|list[tuple]|set[tuple]
        :raise InvalidTypeError: if the pairs to register are not in a dict, list or set
        """
        registry = Registry.instance()

        def _register(key, val):
            if key not in registry:
                registry[key] = val

        if isinstance(prop_value, (dict, list, set)):
            if isinstance(prop_value, dict):
                for prop in prop_value:
                    _register(prop, prop_value[prop])
            else:
                for prop, value in prop_value:
                    _register(prop, value)
        else:
            raise InvalidTypeError(prop_value, (dict, list, set))

    def save_as_attribute(self, name):
        """
        :param name: the name of the attribute to create into the component
        :type name: str
        :return: a function which create an attribute with the specified name into the component
        :rtype: function
        """

        def set_attr(value):
            """Create an attribute with the specified name and value into the component
            :param value: the value to give to the attribute
            """
            self.__setattr__(name, value)

        return set_attr


def iswatcomponent(cls):
    """Check if the specified class is a Wat component
    :param cls: the class you want to know if it is a Wat component
    :type cls: class
    :rtype: bool
    :return: `True` if the specified class is a Wat component, `False` otherwise
    """
    return WatComponent in cls.__bases__ and isinstance(cls, MetaComponent)


def component_from(path):
    """Return the dotted notation name of a component from its path.
     Note that the returned string is ready to be imported.
    :param path: the absolute path of the module you want to convert
    :return: the module package and name in dotted notation
    :rtype: str
    """
    return path.replace(wat.dirs.install, '').replace(os.path.sep, '.')[1:]