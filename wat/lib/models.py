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

__all__ = ['Author']


class Author(object):

    def __init__(self, email, name=None, nickname=None, url=None):
        self.email = str(email).strip().lower()
        if name is not None:
            self.name = name
        if nickname is not None:
            self.nickname = nickname
        if url is not None:
            self.url = url

    def __eq__(self, other):
        return self.email == other.email

    def __repr__(self):
        return "Author(%s)" % self.email

    def __str__(self):
        if self.name:
            string = self.name
            if self.nickname:
                string += " aka %s" % self.nickname
            string += " <%s>" % self.email
        elif self.nickname:
            string = "%s <%s>" % (self.nickname, self.email)
        else:
            string = self.email
        return string