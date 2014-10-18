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

from abc import ABCMeta, abstractmethod, abstractproperty
import os

from it.mrnfrancesco.framework.wat import conf


class AbstractBaseModule(object):
    __metaclass__ = ABCMeta

    # make all non-property class attribute 'read-only'
    def __setattr__(self, key, value):
        if key not in ['name', 'package', 'description']:
            super(AbstractBaseModule, self).__setattr__(key, value)
        else:
            raise AttributeError("'%s.%s' attribute is read-only" % (self.__class__.__name__, key))

    def __init__(self):
        cls = self.__class__
        # create and initialize class variable using subclass provided information
        if not hasattr(cls, 'name'):
            cls.name = cls.__name__
        if not hasattr(cls, 'package'):
            # TODO: check if the following line is right
            # cls.package = cls.__module__
            cls.package = os.getcwd().replace(conf.dirs.modules, '', 1).replace(os.sep, '.')[1:]
        if not hasattr(cls, 'description'):
            cls.description = cls.__doc__

    @property
    def dependencies(self):
        return None

    @abstractproperty
    def provides(self):
        pass

    @abstractproperty
    def authors(self):
        pass

    @abstractproperty
    def release_date(self):
        pass

    @abstractproperty
    def last_update(self):
        pass

    @property
    def version(self):
        return 'unknown'

    @abstractmethod
    def run(self):
        """Run the functional part of the module. It will provide all the information specified if all the dependencies
        were satisfied.
        """
        pass

    def check(self):
        """Check if the module is able to run properly.

        :return: `True` if the module is able to run properly, `False` otherwise
        :rtype: bool
        :raise NotImplementedError: if check method was not implemented
        :raise NotSupportedError: if :method:`self.check()` is not supported for this module
        """
        raise NotImplementedError


# TODO: add :method:verify(), :method:install() and :method:uninstall()
# TODO: convert abstract methods in template methods to do some exception handling (e.g. pycurl.error in run method)