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

from mock import patch, Mock
from sqlalchemy.exc import SQLAlchemyError

from xivo_dao import callfilter_dao
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.callfiltermember import Callfiltermember


class TestCallFilterDAO(DAOTestCase):

    tables = [Callfilter, Callfiltermember]

    def setUp(self):
        self.empty_tables()

    def test_add(self):
        callfilter = Callfilter()
        callfilter.callfrom = 'internal'
        callfilter.type = 'bosssecretary'
        callfilter.bosssecretary = 'bossfirst-serial'
        callfilter.name = 'test'
        callfilter.description = ''

        callfilter_dao.add(callfilter)
        result = self.session.query(Callfilter).first()
        self.assertEquals(result.name, 'test')

    def test_get_by_name(self):
        self._insert_call_filter('test')
        result = callfilter_dao.get_by_name('test')
        self.assertEquals(1, len(result))
        self.assertEquals('test', result[0].name)

    def _insert_call_filter(self, name):
        callfilter = Callfilter()
        callfilter.callfrom = 'internal'
        callfilter.type = 'bosssecretary'
        callfilter.bosssecretary = 'bossfirst-serial'
        callfilter.name = name
        callfilter.description = ''
        self.add_me(callfilter)
        return callfilter.id

    def _add_user_to_filter(self, userid, filterid, role='boss'):
        member = Callfiltermember()
        member.type = 'user'
        member.typeval = str(userid)
        member.callfilterid = filterid
        member.bstype = role
        self.add_me(member)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_add_with_db_error(self, AsteriskSession):
        session = AsteriskSession.return_value = Mock()
        session.commit.side_effect = SQLAlchemyError()

        callfilter = Mock(Callfilter)

        self.assertRaises(SQLAlchemyError, callfilter_dao.add, callfilter)
        session.rollback.assert_called_once_with()

    def test_add_user_to_filter(self):
        filterid = self._insert_call_filter('test')
        callfilter_dao.add_user_to_filter(1, filterid, 'boss')
        member = self.session.query(Callfiltermember).first()
        self.assertEquals('1', member.typeval)
        self.assertEquals('user', member.type)
        self.assertEquals(filterid, member.callfilterid)
        self.assertEquals('boss', member.bstype)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_add_user_to_filter_with_db_error(self, AsteriskSession):
        session = AsteriskSession.return_value = Mock()
        session.commit.side_effect = SQLAlchemyError()

        self.assertRaises(SQLAlchemyError, callfilter_dao.add_user_to_filter, 1, 2, 'boss')
        session.rollback.assert_called_once_with()

    def test_get_callfiltermember_by_userid(self):
        filterid1 = self._insert_call_filter('test1')
        filterid2 = self._insert_call_filter('test2')
        self._add_user_to_filter(1, filterid1)
        self._add_user_to_filter(2, filterid1)
        self._add_user_to_filter(1, filterid2)

        result = callfilter_dao.get_callfiltermembers_by_userid(1)
        self.assertEquals(2, len(result))
        self.assertEquals('1', result[0].typeval)
        self.assertEquals('1', result[1].typeval)

        result = callfilter_dao.get_callfiltermembers_by_userid(2)
        self.assertEquals(1, len(result))
        self.assertEquals('2', result[0].typeval)

    def test_delete_callfiltermember_by_userid(self):
        filterid = self._insert_call_filter('test1')
        self._add_user_to_filter(1, filterid)
        self._add_user_to_filter(2, filterid)

        callfilter_dao.delete_callfiltermember_by_userid(1)

        self.assertEquals(None, self.session.query(Callfiltermember).filter(Callfiltermember.typeval == '1').first())
        self.assertNotEquals(None, self.session.query(Callfiltermember).filter(Callfiltermember.typeval == '2').first())

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_delete_callfiltermember_by_userid_with_db_error(self, AsteriskSession):
        session = AsteriskSession.return_value = Mock()
        session.commit.side_effect = SQLAlchemyError()

        self.assertRaises(SQLAlchemyError, callfilter_dao.delete_callfiltermember_by_userid, 1)
        session.rollback.assert_called_once_with()

    def test_does_secretary_filter_boss_with_no_filters(self):
        boss_id = 1
        secretary_id = 2

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_no_boss_or_secretary(self):
        boss_id = 1
        secretary_id = 2
        self._insert_call_filter('test1')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_no_secretary(self):
        boss_id = 1
        secretary_id = 2
        filter_id = self._insert_call_filter('test1')
        callfilter_dao.add_user_to_filter(boss_id, filter_id, 'boss')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_no_boss(self):
        boss_id = 1
        secretary_id = 2
        filter_id = self._insert_call_filter('test1')
        callfilter_dao.add_user_to_filter(secretary_id, filter_id, 'secretary')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_boss_and_secretary_in_different_filters(self):
        boss_id = 1
        secretary_id = 2
        boss_filter_id = self._insert_call_filter('bossfilter')
        secretatry_filter_id = self._insert_call_filter('secretaryfilter')
        callfilter_dao.add_user_to_filter(boss_id, boss_filter_id, 'boss')
        callfilter_dao.add_user_to_filter(secretary_id, secretatry_filter_id, 'secretary')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertFalse(result)

    def test_does_secretary_filter_boss_with_boss_and_secretary_in_same_filter(self):
        boss_id = 1
        secretary_id = 2
        filter_id = self._insert_call_filter('testfilter')
        callfilter_dao.add_user_to_filter(boss_id, filter_id, 'boss')
        callfilter_dao.add_user_to_filter(secretary_id, filter_id, 'secretary')

        result = callfilter_dao.does_secretary_filter_boss(boss_id, secretary_id)

        self.assertTrue(result)

    def test_does_secretary_filter_boss_with_2_secretaries(self):
        boss_id = 1
        first_secretary_id = 20
        second_secretary_id = 21
        filter_id = self._insert_call_filter('testfilter')
        callfilter_dao.add_user_to_filter(boss_id, filter_id, 'boss')
        callfilter_dao.add_user_to_filter(first_secretary_id, filter_id, 'secretary')
        callfilter_dao.add_user_to_filter(second_secretary_id, filter_id, 'secretary')

        first_result = callfilter_dao.does_secretary_filter_boss(boss_id, first_secretary_id)
        second_result = callfilter_dao.does_secretary_filter_boss(boss_id, second_secretary_id)

        self.assertTrue(first_result)
        self.assertTrue(second_result)

    def test_does_secretary_filter_boss_with_2_bosses(self):
        first_boss_id = 1
        second_boss_id = 2
        secretary_id = 20
        filter_id = self._insert_call_filter('testfilter')
        callfilter_dao.add_user_to_filter(secretary_id, filter_id, 'secretary')
        callfilter_dao.add_user_to_filter(first_boss_id, filter_id, 'boss')
        callfilter_dao.add_user_to_filter(second_boss_id, filter_id, 'boss')

        first_result = callfilter_dao.does_secretary_filter_boss(first_boss_id, secretary_id)
        second_result = callfilter_dao.does_secretary_filter_boss(second_boss_id, secretary_id)

        self.assertTrue(first_result)
        self.assertTrue(second_result)
