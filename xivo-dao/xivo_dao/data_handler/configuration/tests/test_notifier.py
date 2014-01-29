# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

import unittest
from mock import patch, Mock
from xivo_dao.data_handler.configuration import notifier


class TestUserCtiProfileNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd_command = {
                                'ctibus': [],
                                'dird': [],
                                'ipbx': [],
                                'agentbus': [],
                            }

    @patch('xivo_dao.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_bus.resources.configuration.event.LiveRealoadEditedEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_disable_live_reload(self, send_bus_command, LiveRealoadEditedEvent, exec_request_handler):
        new_event = LiveRealoadEditedEvent.return_value = Mock()
        data = {'enabled': False}

        notifier.live_reload_status_changed(data)

        LiveRealoadEditedEvent.assert_called_once_with(False)
        send_bus_command.assert_called_once_with(new_event)
        self.assertFalse(exec_request_handler.called)

    @patch('xivo_dao.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_bus.resources.configuration.event.LiveRealoadEditedEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_enable_live_reload(self, send_bus_command, LiveRealoadEditedEvent, exec_request_handler):
        new_event = LiveRealoadEditedEvent.return_value = Mock()
        data = {'enabled': True}
        self.sysconfd_command['ctibus'] = ['xivo[cticonfig,update]']

        notifier.live_reload_status_changed(data)

        LiveRealoadEditedEvent.assert_called_once_with(True)
        send_bus_command.assert_called_once_with(new_event)
        exec_request_handler.assert_called_once_with(self.sysconfd_command)
