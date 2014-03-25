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

from contextlib import contextmanager
from hamcrest import assert_that, equal_to, instance_of, contains, is_not, \
    none, has_property, contains_inanyorder
from mock import patch

from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementDeletionError
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.func_key import dao
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_type import FuncKeyType as FuncKeyTypeSchema
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser as FuncKeyDestUserSchema
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup as FuncKeyDestGroupSchema
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType as FuncKeyDestinationTypeSchema
from xivo_dao.alchemy.userfeatures import test_dependencies as user_test_dependencies
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.alchemy.groupfeatures import GroupFeatures as GroupSchema


class BaseTestFuncKeyDao(DAOTestCase):

    tables = [
        FuncKeySchema,
        FuncKeyTypeSchema,
        FuncKeyDestinationTypeSchema,
        FuncKeyDestUserSchema,
        FuncKeyDestGroupSchema,
        UserSchema,
        GroupSchema,
    ] + user_test_dependencies

    def setUp(self):
        self.empty_tables()


class TestFuncKeyDao(BaseTestFuncKeyDao):

    destination_type_ids = {
        'user': 1,
        'group': 2,
    }

    destination_type_schemas = {
        'user': (FuncKeyDestUserSchema, 'user_id'),
        'group': (FuncKeyDestGroupSchema, 'group_id'),
    }

    def setUp(self):
        BaseTestFuncKeyDao.setUp(self)
        self.create_types_and_destinations()

    def create_types_and_destinations(self):
        type_row = self.add_func_key_type(name='speeddial')
        self.type_id = type_row.id

        for destination_name, destination_id in self.destination_type_ids.items():
            self.add_func_key_destination_type(id=destination_id, name=destination_name)

    def add_destination(self, destination, destination_id):
        destination_type_id = self.destination_type_ids[destination]
        schema, column = self.destination_type_schemas[destination]

        func_key_row = self.add_func_key(type_id=self.type_id,
                                         destination_type_id=destination_type_id)

        destination_row = schema(**{'func_key_id': func_key_row.id,
                                    column: destination_id})
        self.add_me(destination_row)

        return func_key_row, destination_row

    def prepare_destination(self, destination, destination_id):
        func_key_row, destination_row = self.add_destination(destination, destination_id)

        return FuncKey(id=func_key_row.id,
                       type='speeddial',
                       destination=destination,
                       destination_id=destination_id)

    def find_destination(self, destination, destination_id):
        schema, column_name = self.destination_type_schemas[destination]
        column = getattr(schema, column_name)

        row = (self.session.query(schema)
               .filter(column == destination_id)
               .first())

        return row

    def assert_destination_deleted(self, destination, destination_id):
        row = self.find_destination(destination, destination_id)
        assert_that(row, none())

    @contextmanager
    def mocked_session(self):
        patcher = patch('xivo_dao.helpers.db_manager.AsteriskSession')
        mock = patcher.start()
        yield mock.return_value
        patcher.stop()


class TestFuncKeySearch(TestFuncKeyDao):

    def test_given_no_func_keys_when_searching_then_returns_nothing(self):
        result = dao.search()

        assert_that(result.total, equal_to(0))
        assert_that(result.items, contains())

    def test_given_user_destination_when_searching_then_one_result_returned(self):
        user_row = self.add_user()
        func_key = self.prepare_destination('user', user_row.id)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_given_user_and_group_destination_when_searching_then_two_results_returned(self):
        user_row = self.add_user()
        group_row = self.add_group()
        user_destination = self.prepare_destination('user', user_row.id)
        group_destination = self.prepare_destination('group', group_row.id)

        result = dao.search()
        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains_inanyorder(user_destination, group_destination))

    def test_given_func_key_without_destination_when_searching_then_returns_nothing(self):
        self.add_func_key(type_id=self.type_id,
                          destination_type_id=self.destination_type_ids['user'])

        result = dao.search()
        assert_that(result.total, equal_to(0))
        assert_that(result.items, contains())


class TestFuncKeyFindAllByDestination(TestFuncKeyDao):

    def test_given_no_destinations_then_returns_empty_list(self):
        result = dao.find_all_by_destination('user', 1)

        assert_that(result, contains())

    def test_given_one_user_destination_then_returns_list_with_one_element(self):
        user_row = self.add_user()
        func_key = self.prepare_destination('user', user_row.id)

        result = dao.find_all_by_destination('user', user_row.id)

        assert_that(result, contains(func_key))

    def test_given_2_user_destinations_then_returns_list_with_right_destination(self):
        first_user = self.add_user()
        second_user = self.add_user()

        self.prepare_destination('user', first_user.id)
        func_key = self.prepare_destination('user', second_user.id)

        result = dao.find_all_by_destination('user', second_user.id)

        assert_that(result, contains(func_key))

    def test_given_one_group_destination_then_returns_list_with_one_group_destination(self):
        group_row = self.add_group()
        func_key = self.prepare_destination('group', group_row.id)

        result = dao.find_all_by_destination('group', group_row.id)
        assert_that(result, contains(func_key))

    def test_given_group_and_user_destination_then_returns_list_with_right_destination(self):
        user_row = self.add_user()
        self.prepare_destination('user', user_row.id)
        group_row = self.add_group()
        group_func_key = self.prepare_destination('group', group_row.id)

        result = dao.find_all_by_destination('group', group_row.id)
        assert_that(result, contains(group_func_key))

    def test_given_user_destination_when_searching_wrong_type_then_returns_empty_list(self):
        user_row = self.add_user()
        self.prepare_destination('user', user_row.id)

        result = dao.find_all_by_destination('invalidtype', user_row.id)

        assert_that(result, contains())


class TestFuncKeyGet(TestFuncKeyDao):

    def test_when_no_func_key_then_raises_error(self):
        self.assertRaises(ElementNotExistsError, dao.get, 1)

    def test_when_user_func_key_in_db_then_func_key_model_returned(self):
        user_row = self.add_user()
        func_key = self.prepare_destination('user', user_row.id)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_group_func_key_in_db_then_func_key_model_returned(self):
        group_row = self.add_group()
        func_key = self.prepare_destination('group', group_row.id)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_two_func_keys_in_db_then_right_model_returned(self):
        user_row = self.add_user()

        self.prepare_destination('user', user_row.id)
        second_func_key = self.prepare_destination('user', user_row.id)

        result = dao.get(second_func_key.id)

        assert_that(result, equal_to(second_func_key))


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

    def test_given_group_destination_then_func_key_created(self):
        group_row = self.add_group()

        func_key = FuncKey(type='speeddial',
                           destination='group',
                           destination_id=group_row.id)

        created_func_key = dao.create(func_key)
        assert_that(created_func_key, instance_of(FuncKey))
        assert_that(created_func_key, has_property('id', is_not(none())))

        group_destination_row = self.find_destination('group', group_row.id)
        assert_that(group_destination_row, is_not(none()))

        self.assert_func_key_row_created(group_destination_row)

    @patch('xivo_dao.data_handler.func_key.dao.commit_or_abort')
    def test_given_db_error_then_transaction_rollbacked(self, commit_or_abort):
        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=1)

        with self.mocked_session() as session:
            dao.create(func_key)
            commit_or_abort.assert_any_call(session, ElementCreationError, 'FuncKey')

    def assert_func_key_row_created(self, destination_row):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == destination_row.func_key_id)
               .first())
        assert_that(row, is_not(none()))


class TestFuncKeyDelete(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_deleted(self):
        user_row = self.add_user()
        func_key = self.prepare_destination('user', user_row.id)

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_destination_deleted('user', user_row.id)

    def test_given_group_destination_then_func_key_deleted(self):
        group_row = self.add_group()
        func_key = self.prepare_destination('group', group_row.id)

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_destination_deleted('group', group_row.id)

    @patch('xivo_dao.data_handler.func_key.dao.commit_or_abort')
    def test_given_db_error_then_transaction_rollbacked(self, commit_or_abort):
        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=1)

        with self.mocked_session() as session:
            dao.delete(func_key)
            commit_or_abort.assert_any_call(session, ElementDeletionError, 'FuncKey')

    def assert_func_key_deleted(self, func_key_id):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == func_key_id)
               .first())
        assert_that(row, none())
