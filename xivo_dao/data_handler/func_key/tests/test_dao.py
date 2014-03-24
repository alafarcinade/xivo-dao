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

    def setUp(self):
        BaseTestFuncKeyDao.setUp(self)
        self.create_types_and_destinations()

    def create_types_and_destinations(self):
        func_key_type_row = self.add_func_key_type(name='speeddial')
        user_destination_row = self.add_func_key_destination_type(id=1, name='user')
        group_destination_row = self.add_func_key_destination_type(id=2, name='group')

        self.type_id = func_key_type_row.id
        self.user_destination_id = user_destination_row.id
        self.group_destination_id = group_destination_row.id

    def add_func_key_for_user(self, user_row):
        func_key_row = self.add_func_key(type_id=self.type_id,
                                         destination_type_id=self.user_destination_id)

        dest_user = FuncKeyDestUserSchema(user_id=user_row.id,
                                          func_key_id=func_key_row.id,
                                          destination_type_id=self.user_destination_id)
        self.add_me(dest_user)

        return func_key_row

    def add_func_key_for_group(self, group_row):
        func_key_row = self.add_func_key(type_id=self.type_id,
                                         destination_type_id=self.group_destination_id)

        dest_group = FuncKeyDestGroupSchema(group_id=group_row.id,
                                            func_key_id=func_key_row.id,
                                            destination_type_id=self.group_destination_id)
        self.add_me(dest_group)

        return func_key_row

    def prepare_user_destination(self, user_row):
        func_key_row = self.add_func_key_for_user(user_row)

        return FuncKey(id=func_key_row.id,
                       type='speeddial',
                       destination='user',
                       destination_id=user_row.id)

    def prepare_group_destination(self, group_row):
        func_key_row = self.add_func_key_for_group(group_row)

        return FuncKey(id=func_key_row.id,
                       type='speeddial',
                       destination='group',
                       destination_id=group_row.id)

    def find_user_destination(self, user_id):
        row = (self.session.query(FuncKeyDestUserSchema)
               .filter(FuncKeyDestUserSchema.user_id == user_id)
               .first())

        return row

    def find_group_destination(self, group_id):
        row = (self.session.query(FuncKeyDestGroupSchema)
               .filter(FuncKeyDestGroupSchema.group_id == group_id)
               .first())

        return row

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
        func_key = self.prepare_user_destination(user_row)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_given_user_and_group_destination_when_searching_then_two_results_returned(self):
        user_row = self.add_user()
        group_row = self.add_group()
        user_destination = self.prepare_user_destination(user_row)
        group_destination = self.prepare_group_destination(group_row)

        result = dao.search()
        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains_inanyorder(user_destination, group_destination))

    def test_given_func_key_without_destination_when_searching_then_returns_nothing(self):
        self.add_func_key(type_id=self.type_id,
                          destination_type_id=self.user_destination_id)

        result = dao.search()
        assert_that(result.total, equal_to(0))
        assert_that(result.items, contains())


class TestFuncKeyFindAllByDestination(TestFuncKeyDao):

    def test_given_no_destinations_then_returns_empty_list(self):
        result = dao.find_all_by_destination('user', 1)

        assert_that(result, contains())

    def test_given_one_user_destination_then_returns_list_with_one_element(self):
        user_row = self.add_user()
        func_key = self.prepare_user_destination(user_row)

        result = dao.find_all_by_destination('user', user_row.id)

        assert_that(result, contains(func_key))

    def test_given_2_user_destinations_then_returns_list_with_right_destination(self):
        first_user = self.add_user()
        second_user = self.add_user()

        self.prepare_user_destination(first_user)
        func_key = self.prepare_user_destination(second_user)

        result = dao.find_all_by_destination('user', second_user.id)

        assert_that(result, contains(func_key))

    def test_given_one_group_destination_then_returns_list_with_one_group_destination(self):
        group_row = self.add_group()
        func_key = self.prepare_group_destination(group_row)

        result = dao.find_all_by_destination('group', group_row.id)
        assert_that(result, contains(func_key))

    def test_given_group_and_user_destination_then_returns_list_with_right_destination(self):
        user_row = self.add_user()
        self.prepare_user_destination(user_row)
        group_row = self.add_group()
        group_func_key = self.prepare_group_destination(group_row)

        result = dao.find_all_by_destination('group', group_row.id)
        assert_that(result, contains(group_func_key))

    def test_given_user_destination_when_searching_wrong_type_then_returns_empty_list(self):
        user_row = self.add_user()
        self.prepare_user_destination(user_row)

        result = dao.find_all_by_destination('invalidtype', user_row.id)

        assert_that(result, contains())


class TestFuncKeyGet(TestFuncKeyDao):

    def test_when_no_func_key_then_raises_error(self):
        self.assertRaises(ElementNotExistsError, dao.get, 1)

    def test_when_user_func_key_in_db_then_func_key_model_returned(self):
        user_row = self.add_user()
        func_key = self.prepare_user_destination(user_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_group_func_key_in_db_then_func_key_model_returned(self):
        group_row = self.add_group()
        func_key = self.prepare_group_destination(group_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_two_func_keys_in_db_then_right_model_returned(self):
        user_row = self.add_user()

        self.prepare_user_destination(user_row)
        second_func_key = self.prepare_user_destination(user_row)

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

        user_destination_row = self.find_user_destination(user_row.id)
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

        group_destination_row = self.find_group_destination(group_row.id)
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
        func_key = self.prepare_user_destination(user_row)

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_user_destination_deleted(user_row.id)

    def test_given_group_destination_then_func_key_deleted(self):
        group_row = self.add_group()
        func_key = self.prepare_group_destination(group_row)

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_group_destination_deleted(group_row.id)

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

    def assert_user_destination_deleted(self, user_id):
        row = self.find_user_destination(user_id)
        assert_that(row, none())

    def assert_group_destination_deleted(self, group_id):
        row = self.find_group_destination(group_id)
        assert_that(row, none())
