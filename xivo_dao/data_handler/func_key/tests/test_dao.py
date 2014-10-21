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

from hamcrest import assert_that, equal_to, none, contains, contains_inanyorder, is_not, instance_of, has_property
from mock import patch

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.func_key.tests.test_helpers import FuncKeyHelper

from xivo_dao.data_handler.exception import NotFoundError, DataError
from xivo_dao.data_handler.func_key.model import FuncKey, Hint, Forward
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


class TestFuncKeySearch(TestFuncKeyDao):

    def test_given_no_func_keys_when_searching_then_returns_nothing(self):
        result = dao.search()

        assert_that(result.total, equal_to(0))
        assert_that(result.items, contains())

    def test_given_forward_destination_when_searching_then_one_result_returned(self):
        destination_row = self.create_forward_func_key('_*22.', 'fwdrna')
        func_key = self.row_to_model(destination_row)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_given_service_destination_when_searching_then_one_result_returned(self):
        destination_row = self.create_service_func_key('*98', 'vmusermsg')
        func_key = self.row_to_model(destination_row)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_given_user_destination_when_searching_then_one_result_returned(self):
        destination_row = self.create_user_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_group_destination_when_searching_then_one_result_returned(self):
        destination_row = self.create_group_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_queue_destination_when_searching_then_one_result_returned(self):
        destination_row = self.create_queue_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_conference_destination_when_searching_then_one_result_returned(self):
        destination_row = self.create_conference_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.search()

        assert_that(result.total, equal_to(1))
        assert_that(result.items, contains(func_key))

    def test_given_2_destination_types_when_searching_then_two_results_returned(self):
        user_dest_row = self.create_user_func_key()
        group_dest_row = self.create_group_func_key()

        user_func_key = self.row_to_model(user_dest_row)
        group_func_key = self.row_to_model(group_dest_row)

        result = dao.search()
        assert_that(result.total, equal_to(2))
        assert_that(result.items, contains_inanyorder(user_func_key, group_func_key))

    def test_given_func_key_without_destination_when_searching_then_returns_nothing(self):
        self.add_func_key(type_id=self.speeddial_id,
                          destination_type_id=1)

        result = dao.search()
        assert_that(result.total, equal_to(0))
        assert_that(result.items, contains())


class TestFuncKeyFindAllByDestination(TestFuncKeyDao):

    def test_given_no_destinations_then_returns_empty_list(self):
        result = dao.find_all_by_destination('user', 1)

        assert_that(result, contains())

    def test_given_one_user_destination_then_returns_list_with_one_element(self):
        destination_row = self.create_user_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.find_all_by_destination('user', destination_row.user_id)

        assert_that(result, contains(func_key))

    def test_given_2_user_destinations_then_returns_list_with_right_destination(self):
        first_user_dest = self.create_user_func_key()
        self.create_user_func_key()

        func_key = self.row_to_model(first_user_dest)

        result = dao.find_all_by_destination('user', first_user_dest.user_id)

        assert_that(result, contains(func_key))

    def test_given_one_group_destination_then_returns_list_with_one_group_destination(self):
        destination_row = self.create_group_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.find_all_by_destination('group', destination_row.group_id)
        assert_that(result, contains(func_key))

    def test_given_one_queue_destination_then_returns_list_with_one_queue_destination(self):
        destination_row = self.create_queue_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.find_all_by_destination('queue', destination_row.queue_id)
        assert_that(result, contains(func_key))

    def test_given_one_conference_destination_then_returns_list_with_one_conference_destination(self):
        destination_row = self.create_conference_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.find_all_by_destination('conference', destination_row.conference_id)
        assert_that(result, contains(func_key))

    def test_given_one_service_destination_then_returns_list_with_one_service_destination(self):
        destination_row = self.create_service_func_key('*98', 'vmusermsg')
        func_key = self.row_to_model(destination_row)

        result = dao.find_all_by_destination('service', destination_row.extension_id)

        assert_that(result, contains(func_key))

    def test_given_one_forward_destination_then_returns_list_with_one_forward_destination(self):
        destination_row = self.create_forward_func_key('_*22.', 'fwdrna')
        func_key = self.row_to_model(destination_row)

        result = dao.find_all_by_destination('forward', destination_row.extension_id)

        assert_that(result, contains(func_key))

    def test_given_group_and_user_destination_then_returns_list_with_right_destination(self):
        self.create_user_func_key()
        group_dest_row = self.create_group_func_key()
        group_func_key = self.row_to_model(group_dest_row)

        result = dao.find_all_by_destination('group', group_dest_row.group_id)
        assert_that(result, contains(group_func_key))

    def test_given_user_destination_when_searching_wrong_type_then_returns_empty_list(self):
        destination_row = self.create_user_func_key()
        self.row_to_model(destination_row)

        result = dao.find_all_by_destination('invalidtype', destination_row.user_id)

        assert_that(result, contains())


class TestFuncKeyGet(TestFuncKeyDao):

    def test_when_no_func_key_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, 1)

    def test_when_user_func_key_in_db_then_func_key_model_returned(self):
        destination_row = self.create_user_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_group_func_key_in_db_then_func_key_model_returned(self):
        destination_row = self.create_group_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_queue_func_key_in_db_then_func_key_model_returned(self):
        destination_row = self.create_queue_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_conference_func_key_in_db_then_func_key_model_returned(self):
        destination_row = self.create_conference_func_key()
        func_key = self.row_to_model(destination_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_service_func_key_in_db_then_func_key_model_returned(self):
        destination_row = self.create_service_func_key('*98', 'vmusermsg')
        func_key = self.row_to_model(destination_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_forward_func_key_in_db_then_func_key_model_returned(self):
        destination_row = self.create_forward_func_key('_*22.', 'fwdrna')
        func_key = self.row_to_model(destination_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_two_func_keys_in_db_then_right_model_returned(self):
        self.create_user_func_key()
        second_user_dest = self.create_user_func_key()

        second_func_key = self.row_to_model(second_user_dest)

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
