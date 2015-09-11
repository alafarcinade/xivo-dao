# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.helpers.new_model import NewModel
from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema


class Voicemail(NewModel):

    MANDATORY = [
        'name',
        'number',
        'context'
    ]

    FIELDS = [
        'id',
        'name',
        'number',
        'context',
        'password',
        'email',
        'pager',
        'language',
        'timezone',
        'max_messages',
        'attach_audio',
        'delete_messages',
        'ask_password',
        'enabled',
        'options',
    ]

    _RELATION = {
        'user': 'user'
    }

    @property
    def number_at_context(self):
        return '%s@%s' % (self.number, self.context)


class VoicemailDBConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'uniqueid': 'id',
        'fullname': 'name',
        'mailbox': 'number',
        'context': 'context',
        'pager': 'pager',
        'password': 'password',
        'email': 'email',
        'language': 'language',
        'tz': 'timezone',
        'maxmsg': 'max_messages',
        'options': 'options',
    }

    def __init__(self):
        DatabaseConverter.__init__(self, self.DB_TO_MODEL_MAPPING, VoicemailSchema, Voicemail)

    def to_model(self, source):
        model = DatabaseConverter.to_model(self, source)
        self._convert_model_fields(source, model)

        return model

    def _convert_model_fields(self, source, model):
        model.ask_password = (not source.skipcheckpass)
        model.enabled = (not source.commented)
        model.delete_messages = bool(source.deletevoicemail)

        if source.attach is not None:
            model.attach_audio = bool(source.attach)

        if model.password == '':
            model.password = None

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        self._convert_source_fields(source, model)

        return source

    def update_source(self, source, model):
        DatabaseConverter.update_source(self, source, model)
        self._update_source_fields(source, model)

    def _update_source_fields(self, source, model):
        attach = int(model.attach_audio) if model.attach_audio is not None else None
        password = '' if model.password is None else model.password
        deletevoicemail = int(model.delete_messages)
        skipcheckpass = int(not model.ask_password)
        commented = int(not model.enabled)

        source.attach = attach
        source.deletevoicemail = deletevoicemail
        source.skipcheckpass = skipcheckpass
        source.commented = commented
        source.password = password

    def _convert_source_fields(self, source, model):
        if model.attach_audio is not None:
            source.attach = int(bool(model.attach_audio))
        if model.delete_messages is not None:
            source.deletevoicemail = int(model.delete_messages)
        if model.ask_password is not None:
            source.skipcheckpass = int(not model.ask_password)
        if model.enabled is not None:
            source.commented = int(not model.enabled)
        if model.password is None:
            source.password = ''


db_converter = VoicemailDBConverter()
