# -*- coding: UTF-8 -*-

import unittest
from xivo_dao.helpers import db_manager
from mock import patch, Mock, ANY

class TestDBManager(unittest.TestCase):

    @patch('xivo_dao.helpers.db_manager.create_engine')
    @patch('xivo_dao.helpers.db_manager.sessionmaker')
    def test_connect(self, sessionmaker_mock, create_engine_mock):
        db_manager._DB_URI = "testuri"

        engine_mock = Mock()
        sessionmaker_value = Mock()
        session_mock = Mock()

        create_engine_mock.return_value = engine_mock
        sessionmaker_mock.return_value = sessionmaker_value
        sessionmaker_value.return_value = session_mock

        result = db_manager.connect()

        create_engine_mock.assert_called_once_with("testuri", echo=ANY)
        sessionmaker_mock.assert_called_once_with(bind=engine_mock)
        self.assertEquals(result, session_mock)

    @patch('xivo_dao.helpers.db_manager.connect')
    def test_session_returns_same_session_when_called_twice(self, connect_mock):
        dbsession = Mock()
        connect_mock.return_value = dbsession

        result1 = db_manager.session()
        self.assertEquals(result1, dbsession)

        result2 = db_manager.session()
        self.assertEquals(result2, dbsession)