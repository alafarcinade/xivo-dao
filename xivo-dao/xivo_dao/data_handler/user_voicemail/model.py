# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.helpers.new_model import NewModel

DB_TO_MODEL_MAPPING = {
    'user_id': 'user_id',
    'voicemail_id': 'voicemail_id',
    'enablevoicemail': 'enabled',
}


class UserVoicemail(NewModel):

    def __init__(self, *args, **kwargs):
        NewModel.__init__(self, *args, **kwargs)
        if self.enabled is None:
            self.enabled = True

    FIELDS = [
        'user_id',
        'voicemail_id',
        'enabled'
    ]

    MANDATORY = [
        'user_id',
        'voicemail_id',
    ]

    _RELATION = {}


class UserVoicemailDbConverter(DatabaseConverter):

    def __init__(self):
        DatabaseConverter.__init__(self, DB_TO_MODEL_MAPPING, None, UserVoicemail)

    def to_model(self, db_row):
        model = DatabaseConverter.to_model(self, db_row)
        model.enabled = bool(model.enabled)
        return model

    def to_source(self, model):
        db_row = DatabaseConverter.to_source(self, model)
        db_row.enablevoicemail = int(db_row.enablevoicemail)
        return db_row


db_converter = UserVoicemailDbConverter()
