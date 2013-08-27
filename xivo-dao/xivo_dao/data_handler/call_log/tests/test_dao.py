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

from datetime import datetime, timedelta
from hamcrest import assert_that, contains_inanyorder, equal_to, has_length, has_property
from mock import Mock, patch
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.data_handler.call_log import dao as call_log_dao
from xivo_dao.data_handler.call_log.model import CallLog
from xivo_dao.data_handler.exception import ElementCreationError, ElementDeletionError
from xivo_dao.tests.test_dao import DAOTestCase


class TestCallLogDAO(DAOTestCase):

    tables = [
        CallLogSchema,
    ]

    def setUp(self):
        self.empty_tables()

    def tearDown(self):
        pass

    def test_find_all_not_found(self):
        expected_result = []

        result = call_log_dao.find_all()

        assert_that(result, equal_to(expected_result))

    def test_find_all_found(self):
        call_logs = call_log_1, call_log_2 = [CallLog(date=datetime.today(), duration=timedelta(0)),
                                              CallLog(date=datetime.today(), duration=timedelta(1))]
        call_log_dao.create_all(call_logs)

        result = call_log_dao.find_all()

        assert_that(result, has_length(2))

    def test_find_all_in_period_not_found(self):
        expected_result = []
        start, end = datetime(2013, 1, 1), datetime(2013, 2, 1)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, equal_to(expected_result))

    def test_find_all_in_period_found(self):
        call_logs = _, call_log_1, call_log_2, _ = (CallLog(date=datetime(2013, 1, 1), duration=timedelta(0)),
                                                    CallLog(date=datetime(2013, 1, 2), duration=timedelta(1)),
                                                    CallLog(date=datetime(2013, 1, 3), duration=timedelta(2)),
                                                    CallLog(date=datetime(2013, 1, 4), duration=timedelta(3)))
        start = datetime(2013, 1, 1, 12)
        end = datetime(2013, 1, 3, 12)
        call_log_dao.create_all(call_logs)

        result = call_log_dao.find_all_in_period(start, end)

        assert_that(result, has_length(2))
        assert_that(result, contains_inanyorder(has_property('date', call_log_1.date),
                                                has_property('date', call_log_2.date)))

    def test_create_all(self):
        call_logs = call_log_1, call_log_2 = [CallLog(date=datetime.today(), duration=timedelta(0)),
                                              CallLog(date=datetime.today(), duration=timedelta(1))]

        call_log_dao.create_all(call_logs)

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, has_length(2))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_all_db_error(self, session_init):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        session_init.return_value = session

        call_logs = call_log_1, call_log_2 = [CallLog(date=datetime.today(), duration=timedelta(0)),
                                              CallLog(date=datetime.today(), duration=timedelta(1))]

        self.assertRaises(ElementCreationError, call_log_dao.create_all, call_logs)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete_all(self):
        call_logs = [CallLog(date=datetime.today(), duration=timedelta(0)),
                     CallLog(date=datetime.today(), duration=timedelta(1))]
        call_log_dao.create_all(call_logs)

        call_log_dao.delete_all()

        call_log_rows = self.session.query(CallLogSchema).all()
        assert_that(call_log_rows, has_length(0))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_delete_all_db_error(self, session_init):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        session_init.return_value = session

        self.assertRaises(ElementDeletionError, call_log_dao.delete_all)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()
