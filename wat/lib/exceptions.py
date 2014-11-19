# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#   3. Neither the name of Django nor the names of its contributors may be used
#      to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = {
    # generic
    'WatError', 'ComponentError', 'PropertyError'
    # failure
    'ComponentFailure',
    # missing
    'PropertyDoesNotExist',
    # misconfigured
    'ImproperlyConfigured',
    # invalid
    'InvalidTypeError',
}

from functools import reduce
import operator


class WatError(Exception):
    """A generic WAT Framework error"""

    def __init__(self, message, params=None, code=None):
        """
        The `message` argument can be a single error, a list of errors, or a
        dictionary that maps field names to lists of errors. What we define as
        an "error" can be either a simple string or an instance of
        ValidationError with its message attribute set, and what we define as
        list or dictionary can be an actual `list` or `dict` or an instance
        of WatError with its `error_list` or `error_dict` attribute set.
        """

        super(WatError, self).__init__(message, params, code)

        if isinstance(message, WatError):
            if hasattr(message, 'error_dict'):
                message = message.error_dict
            elif not hasattr(message, 'code'):
                message = message.error_list
            else:
                message, params, code = message.message, message.params, message.code

        if isinstance(message, dict):
            self.error_dict = {}
            for field, messages in message.items():
                if not isinstance(messages, WatError):
                    messages = WatError(messages)
                self.error_dict[field] = messages.error_list

        elif isinstance(message, list):
            self.error_list = []
            for message in message:
                # Normalize plain strings to instances of WatError.
                if not isinstance(message, WatError):
                    message = WatError(message)
                self.error_list.extend(message.error_list)

        else:
            self.message = message
            self.params = params
            self.code = code
            self.error_list = [self]

    @property
    def message_dict(self):
        """
        :return: a dictionary of collected errors
        :rtype: dict
        :raise AttributeError: if this WatError doesn't have an error_dict
        """
        getattr(self, 'error_dict')

        return dict(self)

    @property
    def messages(self):
        if hasattr(self, 'error_dict'):
            return reduce(operator.add, dict(self).values())
        return list(self)

    def update_error_dict(self, error_dict):
        if hasattr(self, 'error_dict'):
            for field, error_list in self.error_dict.items():
                error_dict.setdefault(field, []).extend(error_list)
        else:
            error_dict.setdefault('__all__', []).extend(self.error_list)
        return error_dict

    def __iter__(self):
        if hasattr(self, 'error_dict'):
            for field, errors in self.error_dict.items():
                yield field, list(WatError(errors))
        else:
            for error in self.error_list:
                message = error.message
                if error.params:
                    message %= error.params
                yield message

    def __str__(self):
        if hasattr(self, 'error_dict'):
            return repr(dict(self))
        return repr(list(self))

    def __repr__(self):
        return 'WatError(%s)' % self


class ComponentError(WatError):
    """The component encounter an error"""


class PropertyError(WatError):
    """The property encounter an error"""


class PropertyDoesNotExist(PropertyError):
    """The requested property does not exist"""

    def __init__(self, message, params=None):
        super(PropertyDoesNotExist, self).__init__(message, params, code='missing')


class ComponentFailure(ComponentError):
    """The module failed during execution"""

    def __init__(self, message, params=None):
        super(ComponentFailure, self).__init__(message, params, code='failure')


class ImproperlyConfigured(WatError):
    """WAT Framework is somehow improperly configured"""

    def __init__(self, message, params=None):
        super(ImproperlyConfigured, self).__init__(message, params, code='misconfigured')


class InvalidTypeError(WatError, TypeError):
    """The specified parameter type is unexpected"""
    def __init__(self, param, expected):
        if isinstance(expected, (list, tuple, set)):
            super(InvalidTypeError, self).__init__(
                message="%(param_type)s is not an instance or a subclass of %(expected)s",
                params={
                    'param_type': type(param),
                    'expected': '|'.join([expected_type.__name__ for expected_type in expected])
                },
                code='invalid'
            )
        else:
            raise InvalidTypeError(param=expected, expected=(list, set, tuple))