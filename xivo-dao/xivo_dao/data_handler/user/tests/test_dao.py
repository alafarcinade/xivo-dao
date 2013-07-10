# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from hamcrest import assert_that, equal_to, has_length, has_property, all_of, has_items, contains
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user.model import UserOrdering
from xivo_dao.tests.test_dao import DAOTestCase
from mock import patch, Mock
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.exception import ElementEditionError, \
    ElementCreationError


class TestUserDAO(DAOTestCase):

    tables = [
        AgentFeatures,
        Callfilter,
        Callfiltermember,
        ContextInclude,
        CtiPhoneHintsGroup,
        CtiPresences,
        CtiProfile,
        Dialaction,
        LineSchema,
        PhoneFunckey,
        QueueMember,
        RightCallMember,
        SchedulePath,
        UserSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_find_all_no_users(self):
        expected = []
        users = user_dao.find_all()

        assert_that(users, equal_to(expected))

    def test_find_all_one_user(self):
        firstname = 'Pascal'
        user_id = self._insert_user(firstname=firstname)

        users = user_dao.find_all()
        assert_that(users, has_length(1))

        user_found = users[0]
        assert_that(user_found, has_property('id', user_id))
        assert_that(user_found, has_property('firstname', firstname))

    def test_find_all_two_users(self):
        firstname1 = 'Pascal'
        firstname2 = 'George'

        user1_id = self._insert_user(firstname=firstname1)
        user2_id = self._insert_user(firstname=firstname2)

        users = user_dao.find_all()
        assert_that(users, has_length(2))

        assert_that(users, has_items(
            all_of(
                has_property('id', user1_id),
                has_property('firstname', firstname1)),
            all_of(
                has_property('id', user2_id),
                has_property('firstname', firstname2))
        ))

    def test_find_all_default_order_by_lastname_firstname(self):
        user_id1 = self._insert_user(firstname='Jules', lastname='Santerre')
        user_id2 = self._insert_user(firstname='Vicky', lastname='Bourbon')
        user_id3 = self._insert_user(firstname='Anne', lastname='Bourbon')

        users = user_dao.find_all()
        assert_that(users, has_length(3))

        assert_that(users[0].id, equal_to(user_id3))
        assert_that(users[1].id, equal_to(user_id2))
        assert_that(users[2].id, equal_to(user_id1))

    def test_find_all_order_by_firstname(self):
        user_id_last = self._insert_user(firstname='Bob', lastname='Alzard')
        user_id_first = self._insert_user(firstname='Albert', lastname='Breton')

        users = user_dao.find_all(order=[UserOrdering.firstname])

        assert_that(users[0].id, equal_to(user_id_first))
        assert_that(users[1].id, equal_to(user_id_last))

    def test_find_all_order_by_lastname(self):
        user_id_last = self._insert_user(firstname='Albert', lastname='Breton')
        user_id_first = self._insert_user(firstname='Bob', lastname='Alzard')

        users = user_dao.find_all(order=[UserOrdering.lastname])

        assert_that(users[0].id, equal_to(user_id_first))
        assert_that(users[1].id, equal_to(user_id_last))

    def test_find_user_no_user(self):
        result = user_dao.find_user('abc', 'def')

        assert_that(result, equal_to(None))

    def test_find_user_not_right_firstname(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        wrong_firstname = 'Gregory'

        self._insert_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_user(wrong_firstname, lastname)

        assert_that(result, equal_to(None))

    def test_find_user(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        user_id = self._insert_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_user('Lord', 'Sanderson')

        assert_that(result, all_of(
            has_property('id', user_id),
            has_property('firstname', firstname),
            has_property('lastname', lastname)
        ))

    def test_find_user_two_users_same_name(self):
        firstname = 'Lord'
        lastname = 'Sanderson'

        user_id1 = self._insert_user(firstname=firstname, lastname=lastname)
        self._insert_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_user(firstname, lastname)

        assert_that(result, has_property('id', user_id1))

    def test_find_all_by_fullname_no_users(self):
        result = user_dao.find_all_by_fullname('')

        assert_that(result, has_length(0))

    def test_find_all_by_fullname(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        fullname = '%s %s' % (firstname, lastname)

        user_id = self._insert_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_all_by_fullname(fullname)

        assert_that(result, has_length(1))
        assert_that(result, contains(
            all_of(
                has_property('id', user_id),
                has_property('firstname', firstname),
                has_property('lastname', lastname)
            )))

    def test_find_all_by_fullname_lowercase(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        fullname = '%s %s' % (firstname, lastname)

        user_id = self._insert_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_all_by_fullname(fullname.lower())

        assert_that(result, has_length(1))
        assert_that(result, contains(
            all_of(
                has_property('id', user_id),
                has_property('firstname', firstname),
                has_property('lastname', lastname)
            )))

    def test_find_all_by_fullname_partial(self):
        firstname = 'Lord'
        lastname = 'Sanderson'
        partial_fullname = 'd san'

        user_id = self._insert_user(firstname=firstname, lastname=lastname)

        result = user_dao.find_all_by_fullname(partial_fullname)

        assert_that(result, has_length(1))
        assert_that(result, contains(
            all_of(
                has_property('id', user_id),
                has_property('firstname', firstname),
                has_property('lastname', lastname)
            )))

    def test_find_all_by_fullname_two_users_default_order(self):
        search_term = 'lord'

        user_id_last = self._insert_user(firstname='Lord', lastname='Sanderson')
        user_id_first = self._insert_user(firstname='Great', lastname='Lord')
        self._insert_user(firstname='Toto', lastname='Tata')

        result = user_dao.find_all_by_fullname(search_term)

        assert_that(result, has_length(2))
        assert_that(result, contains(
            has_property('id', user_id_first),
            has_property('id', user_id_last),
        ))

    def test_get_inexistant(self):
        self.assertRaises(LookupError, user_dao.get, 42)

    def test_get(self):
        user_id = self._insert_user(firstname='Paul')

        user = user_dao.get(user_id)

        assert_that(user.id, equal_to(user_id))

    def test_get_commented(self):
        user_id = self._insert_user(firstname='Robert', commented=1)

        self.assertRaises(LookupError, user_dao.get, user_id)

    def test_get_by_number_context(self):
        context, number = 'default', '1234'
        user_id = self._insert_user(firstname='Robert')
        self._insert_line(iduserfeatures=user_id, number=number, context=context)

        user = user_dao.get_by_number_context(number, context)

        assert_that(user.id, equal_to(user_id))

    def test_get_by_number_context_line_commented(self):
        context, number = 'default', '1234'
        user_id = self._insert_user(firstname='Robert')
        self._insert_line(iduserfeatures=user_id,
                          number=number,
                          context=context,
                          commented=1)

        self.assertRaises(LookupError, user_dao.get_by_number_context, number, context)

    def _insert_line(self, **kwargs):
        kwargs.setdefault('protocolid', 0)
        kwargs.setdefault('name', 'chaise')
        kwargs.setdefault('provisioningid', 0)
        line = LineSchema(**kwargs)
        self.add_me(line)

    def _insert_user(self, **kwargs):
        user = UserSchema(**kwargs)
        self.add_me(user)
        return user.id

    def test_create(self):
        user = User(firstname='toto',
                    lastname='kiki',
                    language='fr_FR')

        created_user = user_dao.create(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.firstname == user.firstname)
               .filter(UserSchema.lastname == user.lastname)
               .first())

        self.assertEquals(row.id, created_user.id)
        self.assertEquals(row.firstname, user.firstname)
        self.assertEquals(row.lastname, user.lastname)
        self.assertEquals(row.language, user.language)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        user = User(firstname='toto',
                    lastname='kiki',
                    language='fr_FR')

        self.assertRaises(ElementCreationError, user_dao.create, user)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_edit(self):
        firstname = 'Robert'
        lastname = 'Raleur'
        expected_lastname = 'Lereu'
        user_id = self._insert_user(firstname=firstname, lastname=lastname)

        user = User(id=user_id, lastname=expected_lastname)

        user_dao.edit(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.id == user_id)
               .first())

        self.assertEquals(row.firstname, firstname)
        self.assertEquals(row.lastname, expected_lastname)

    def test_edit_with_unknown_user(self):
        user = User(id=123, lastname='unknown')

        self.assertRaises(ElementEditionError, user_dao.edit, user)

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_edit_with_database_error(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        user = User(id=123,
                    firstname='toto',
                    lastname='kiki',
                    language='fr_FR')

        self.assertRaises(ElementEditionError, user_dao.edit, user)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete(self):
        firstname = 'Gadou'
        lastname = 'Pipo'
        user_id = self._insert_user(firstname=firstname, lastname=lastname)

        user = user_dao.get(user_id)

        user_dao.delete(user)

        row = (self.session.query(UserSchema)
               .filter(UserSchema.id == user_id)
               .first())

        self.assertEquals(row, None)
