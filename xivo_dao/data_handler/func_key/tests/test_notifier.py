# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.func_key.model import UserFuncKey
from xivo_dao.data_handler.func_key import notifier

from mock import patch, Mock


class TestNotifier(TestCase):

    @patch('xivo_bus.resources.func_key.event.UserCreateFuncKeyEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_create_user_func_key(self, send_bus_command, UserCreateFuncKeyEvent):
        new_event = UserCreateFuncKeyEvent.return_value = Mock()

        func_key = UserFuncKey(id=1, user_id=2)

        notifier.created(func_key)

        UserCreateFuncKeyEvent.assert_called_once_with(func_key.id,
                                                       func_key.user_id)

        send_bus_command.assert_called_once_with(new_event)

    @patch('xivo_bus.resources.func_key.event.UserDeleteFuncKeyEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_delete_user_func_key(self, send_bus_command, UserDeleteFuncKeyEvent):
        new_event = UserDeleteFuncKeyEvent.return_value = Mock()

        func_key = UserFuncKey(id=1, user_id=2)

        notifier.deleted(func_key)

        UserDeleteFuncKeyEvent.assert_called_once_with(func_key.id,
                                                       func_key.user_id)

        send_bus_command.assert_called_once_with(new_event)
