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

from xivo_dao.data_handler.user.services import UserNotFoundError
from xivo_dao.data_handler.voicemail.dao import VoicemailNotFoundError
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.voicemail import dao as voicemail_dao


def associate_voicemail(user_id, voicemail_id):
    try:
        user = user_dao.get_user_by_id(user_id)
    except LookupError:
        raise UserNotFoundError(user_id)
    try:
        voicemail = voicemail_dao.get_voicemail_by_id(voicemail_id)
    except LookupError:
        raise VoicemailNotFoundError(voicemail_id)

    voicemail.user = user

    voicemail_dao.edit(voicemail)
