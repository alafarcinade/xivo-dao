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

from xivo_bus.resources.user_voicemail import event
from xivo_dao.data_handler.user_line_extension import dao as user_line_dao
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers import bus_manager


def associated(user_voicemail):
    sysconf_command_associated(user_voicemail)
    bus_event_associated(user_voicemail)


def sysconf_command_associated(user_voicemail):
    command = {
        'dird': [],
        'ipbx': ['sip reload'],
        'agentbus': [],
        'ctibus': _generate_ctibus_commands(user_voicemail)
    }
    sysconfd_connector.exec_request_handlers(command)


def _generate_ctibus_commands(user_voicemail):
    ctibus = ['xivo[user,edit,%d]' % user_voicemail.user_id]

    user_lines = user_line_dao.find_all_by_user_id(user_voicemail.user_id)
    for user_line in user_lines:
        ctibus.append('xivo[phone,edit,%d]' % user_line.line_id)

    return ctibus


def bus_event_associated(user_voicemail):
    bus_event = event.UserVoicemailAssociatedEvent(user_voicemail.user_id,
                                                   user_voicemail.voicemail_id,
                                                   user_voicemail.enabled)
    bus_manager.send_bus_command(bus_event)
