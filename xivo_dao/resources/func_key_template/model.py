# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from collections import namedtuple

from xivo_dao.helpers import errors

from xivo_dao.helpers.new_model import NewModel


class FuncKeyTemplate(NewModel):

    FIELDS = ['id',
              'name',
              'private',
              'keys']

    MANDATORY = []

    _RELATION = {}

    def __init__(self, **parameters):
        parameters.setdefault('keys', {})
        parameters.setdefault('private', False)
        super(FuncKeyTemplate, self).__init__(**parameters)

    def merge(self, other):
        keys = dict(self.keys)
        other_keys = other.keys
        keys.update(other_keys)
        return FuncKeyTemplate(keys=keys)

    def get(self, position):
        if position not in self.keys:
            raise errors.not_found('FuncKey', template_id=self.id, position=position)
        return self.keys[position]


UserTemplate = namedtuple('UserTemplate', ['user_id', 'template_id'])
