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

from mock import patch, Mock
from hamcrest import assert_that, contains, equal_to

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.func_key import services
from xivo_dao.data_handler.func_key.model import UserFuncKey, Forward
from xivo_dao.data_handler.user.model import User


class TestFuncKeyService(TestCase):

    @patch('xivo_dao.data_handler.func_key.dao.find_all_forwards')
    def test_find_all_fwd_unc(self, find_all_forwards):
        expected_number = '1234'
        fwd_type = 'unconditional'
        user_id = 1

        find_all_forwards.return_value = [Forward(user_id=user_id,
                                                  type=fwd_type,
                                                  number=expected_number),
                                          Forward(user_id=user_id,
                                                  type=fwd_type,
                                                  number=None)]

        result = services.find_all_fwd_unc(user_id)

        find_all_forwards.assert_called_once_with(user_id, fwd_type)
        assert_that(result, contains(expected_number, ''))

    @patch('xivo_dao.data_handler.func_key.dao.find_all_forwards')
    def test_find_all_fwd_rna(self, find_all_forwards):
        expected_number = '2345'
        fwd_type = 'noanswer'
        user_id = 1

        find_all_forwards.return_value = [Forward(user_id=user_id,
                                                  type=fwd_type,
                                                  number=expected_number),
                                          Forward(user_id=user_id,
                                                  type=fwd_type,
                                                  number=None)]

        result = services.find_all_fwd_rna(user_id)

        find_all_forwards.assert_called_once_with(user_id, fwd_type)
        assert_that(result, contains(expected_number, ''))

    @patch('xivo_dao.data_handler.func_key.dao.find_all_forwards')
    def test_find_all_fwd_busy(self, find_all_forwards):
        expected_number = '1234'
        fwd_type = 'busy'
        user_id = 1

        find_all_forwards.return_value = [Forward(user_id=user_id,
                                                  type=fwd_type,
                                                  number=expected_number),
                                          Forward(user_id=user_id,
                                                  type=fwd_type,
                                                  number=None)]

        result = services.find_all_fwd_busy(user_id)

        find_all_forwards.assert_called_once_with(user_id, fwd_type)
        assert_that(result, contains(expected_number, ''))


@patch('xivo_dao.data_handler.func_key.notifier.created')
@patch('xivo_dao.data_handler.func_key.dao.create')
class TestCreateUserDestination(TestCase):

    def test_create_user_destination(self,
                                     dao_create,
                                     notifier_create):
        user = Mock(User, id=1)
        func_key = UserFuncKey(user_id=user.id)

        result = services.create_user_destination(user)

        assert_that(result, equal_to(dao_create.return_value))
        dao_create.assert_called_once_with(func_key)
        notifier_create.assert_called_once_with(dao_create.return_value)


@patch('xivo_dao.data_handler.func_key.notifier.deleted')
@patch('xivo_dao.data_handler.func_key.dao.delete')
@patch('xivo_dao.data_handler.func_key_template.dao.remove_func_key_from_templates')
@patch('xivo_dao.data_handler.func_key.dao.find_user_destination')
class TestDeleteUserDestination(TestCase):

    def test_delete_user_destination(self,
                                     find_user_destination,
                                     remove_func_key_from_templates,
                                     dao_delete,
                                     notifier_delete):
        user = Mock(User, id=1)
        func_key = UserFuncKey(user_id=user.id)

        find_user_destination.return_value = func_key

        services.delete_user_destination(user)

        find_user_destination.assert_called_once_with(user.id)
        dao_delete.assert_called_once_with(func_key)
        remove_func_key_from_templates.assert_called_once_with(func_key)
        notifier_delete.assert_called_once_with(func_key)

    def test_delete_user_destination_when_destination_does_not_exist(self,
                                                                     find_user_destination,
                                                                     remove_func_key_from_templates,
                                                                     dao_delete,
                                                                     notifier_delete):
        user = Mock(User, id=1)

        find_user_destination.return_value = None

        services.delete_user_destination(user)

        find_user_destination.assert_called_once_with(user.id)
        self.assertNotCalled(dao_delete)
        self.assertNotCalled(remove_func_key_from_templates)
        self.assertNotCalled(notifier_delete)
