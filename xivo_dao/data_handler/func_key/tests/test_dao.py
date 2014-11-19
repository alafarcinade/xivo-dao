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

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that, none, contains, is_not, instance_of, has_property
from mock import patch

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.func_key.tests.test_helpers import FuncKeyHelper

from xivo_dao.data_handler.exception import DataError
from xivo_dao.data_handler.func_key.model import FuncKey, Forward
from xivo_dao.data_handler.func_key import dao
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.tests.helpers.session import mocked_dao_session


class TestFuncKeyDao(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestFuncKeyDao, self).setUp()
        self.setup_funckeys()

    def row_to_model(self, row):
        return FuncKey(id=row.func_key_id,
                       type='speeddial',
                       destination=self._destination_name(row.destination_type_id),
                       destination_id=self._destination_id(row))

    def _destination_name(self, type_id):
        for name, destination in self.destinations.items():
            if destination[2] == type_id:
                return name

    def _destination_id(self, row):
        for name, destination in self.destinations.items():
            if destination[2] == row.destination_type_id:
                return getattr(row, destination[1])


class TestFuncKeyCreate(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_created(self):
        user_row = self.add_user()

        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=user_row.id)

        created_func_key = dao.create(func_key)
        assert_that(created_func_key, instance_of(FuncKey))
        assert_that(created_func_key, has_property('id', is_not(none())))

        user_destination_row = self.find_destination('user', user_row.id)
        assert_that(user_destination_row, is_not(none()))

        self.assert_func_key_row_created(user_destination_row)

    @mocked_dao_session
    @patch('xivo_dao.data_handler.func_key.dao.commit_or_abort')
    def test_given_db_error_then_transaction_rollbacked(self, session, commit_or_abort):
        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=1)

        dao.create(func_key)
        commit_or_abort.assert_any_call(session, DataError.on_create, 'FuncKey')

    def assert_func_key_row_created(self, destination_row):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == destination_row.func_key_id)
               .first())
        assert_that(row, is_not(none()))


class TestFuncKeyDelete(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_deleted(self):
        destination_row = self.create_user_func_key()
        func_key = self.row_to_model(destination_row)

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_destination_deleted('user', destination_row.user_id)

    @mocked_dao_session
    @patch('xivo_dao.data_handler.func_key.dao.commit_or_abort')
    def test_given_db_error_then_transaction_rollbacked(self, session, commit_or_abort):
        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=1)

        dao.delete(func_key)

        commit_or_abort.assert_any_call(session, DataError.on_delete, 'FuncKey')

    def assert_func_key_deleted(self, func_key_id):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == func_key_id)
               .first())
        assert_that(row, none())


class TestFindAllForwards(TestFuncKeyDao):

    def prepare_user_and_forward(self, exten, fwd_type, number=None):
        user_row = self.add_user()

        exten_row = self.add_extenfeatures(exten, fwd_type)
        forward_row = self.add_forward_destination(exten_row.id, number)
        self.add_func_key_mapping(func_key_id=forward_row.func_key_id,
                                  destination_type_id=forward_row.destination_type_id,
                                  template_id=user_row.func_key_private_template_id,
                                  position=1,
                                  blf=True)

        return user_row, forward_row

    def test_given_no_forwards_then_returns_empty_list(self):
        result = dao.find_all_forwards(1, 'unconditional')

        assert_that(result, contains())

    def test_given_unconditional_forward_then_list_contains_unconditional_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*21.', 'fwdunc', number)

        result = dao.find_all_forwards(user_row.id, 'unconditional')

        assert_that(result, contains(Forward(user_id=user_row.id,
                                             type='unconditional',
                                             number=number)))

    def test_given_noanswer_forward_then_list_contains_noanswer_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*22.', 'fwdrna', number)

        result = dao.find_all_forwards(user_row.id, 'noanswer')

        assert_that(result, contains(Forward(user_id=user_row.id,
                                             type='noanswer',
                                             number=number)))

    def test_given_busy_forward_then_list_contains_busy_forward(self):
        number = '1234'
        user_row, forward_row = self.prepare_user_and_forward('_*23.', 'fwdbusy', number)

        result = dao.find_all_forwards(user_row.id, 'busy')

        assert_that(result, contains(Forward(user_id=user_row.id,
                                             type='busy',
                                             number=number)))
