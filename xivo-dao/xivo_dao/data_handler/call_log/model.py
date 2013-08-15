# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers.abstract_model import AbstractModels


class CallLog(AbstractModels):
    MANDATORY = [
        'date',
        'duration',
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'date': 'date',
        'source_name': 'source_name',
        'source_exten': 'source_exten',
        'destination_name': 'destination_name',
        'destination_exten': 'destination_exten',
        'user_field': 'user_field',
        'answered': 'answered',
        'duration': 'duration',
    }

    _RELATION = {
    }