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