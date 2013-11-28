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

from xivo_bus.resources.user_line import event
from xivo_dao.data_handler.user_line_extension import dao as user_line_dao
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers import bus_manager


def associated(user_line):
    sysconf_command_association_updated(user_line)
    bus_event_associated(user_line)


def dissociated(user_line):
    sysconf_command_association_updated(user_line)
    bus_event_dissociated(user_line)


def sysconf_command_association_updated(user_line):
    command = {
        'dird': [],
        'ipbx': ['sip reload'],
        'agentbus': [],
        'ctibus': _generate_ctibus_commands(user_line)
    }
    sysconfd_connector.exec_request_handlers(command)


def _generate_ctibus_commands(user_line):
    ctibus = ['xivo[user,edit,%d]' % user_line.user_id]

    user_lines = user_line_dao.find_all_by_user_id(user_line.user_id)
    for user_line in user_lines:
        ctibus.append('xivo[phone,edit,%d]' % user_line.line_id)

    return ctibus


def bus_event_associated(user_line):
    bus_event = event.UserLineAssociatedEvent(user_line.user_id,
                                              user_line.line_id,
                                              user_line.main_user,
                                              user_line.main_line)
    bus_manager.send_bus_command(bus_event)


def bus_event_dissociated(user_line):
    bus_event = event.UserLineDissociatedEvent(user_line.user_id,
                                               user_line.line_id,
                                              user_line.main_user,
                                              user_line.main_line)
    bus_manager.send_bus_command(bus_event)
