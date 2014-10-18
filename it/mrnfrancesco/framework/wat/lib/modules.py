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


from datetime import date

from it.mrnfrancesco.framework.wat.lib.models import Author
from it.mrnfrancesco.framework.wat.lib.properties import Property, Constraint, Operation


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
            if all(isinstance(spec, (Property, Operation)) for spec in provides):
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

    @staticmethod
    def check():
        """Check if the module is able to run properly.

        :return: `True` if the module is able to run properly, `False` otherwise
        :rtype: bool
        :raise NotImplementedError: if check method was not implemented
        :raise NotSupportedError: if :method:`self.check()` is not supported for this module
        """
        raise NotImplementedError

    @staticmethod
    def run():
        raise NotImplementedError

# TODO: add :method:verify(), :method:install() and :method:uninstall()