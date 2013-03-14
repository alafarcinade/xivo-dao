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


from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.alchemy.ldapserver import LdapServer
from xivo_dao import ldap_dao


class TestLdapDAO(DAOTestCase):

    tables = [LdapServer, LdapFilter]

    def setUp(self):
        self.empty_tables()

    def test_get_ldapserver_with_id(self):

        ldapserver = self._insert_ldapserver(name='ldapserver_test')

        ldapserver_result = ldap_dao.get_ldapserver_with_id(ldapserver.id)

        self.assertEqual(ldapserver.id, ldapserver_result.id)

    def test_get_ldapfilter_with_name(self):

        ldapserver = self._insert_ldapserver(name='ldapserver_test')
        ldapfilter = self._insert_ldapfilter(ldapserver.id, name='ldapfilter_test')

        ldapfilter_result = ldap_dao.get_ldapfilter_with_name(ldapfilter.name)

        self.assertEqual(ldapfilter.name, ldapfilter_result.name)

    def _insert_ldapfilter(self, ldapserver_id, name='ldapfilter_test'):
        ldap = LdapFilter()
        ldap.ldapserverid = ldapserver_id
        ldap.name = name
        ldap.user = 'user'
        ldap.passwd = 'passwd'
        ldap.additionaltype = 'office'
        ldap.description = 'description'

        self.session.begin()
        self.session.add(ldap)
        self.session.commit()

        return ldap

    def _insert_ldapserver(self, name='ldapserver_test'):
        ldapserver = LdapServer()
        ldapserver.name = name
        ldapserver.host = 'test-ldap-server'
        ldapserver.port = 389
        ldapserver.securitylayer = 'tls'
        ldapserver.protocolversion = '3'
        ldapserver.description = 'description'

        self.session.begin()
        self.session.add(ldapserver)
        self.session.commit()

        return ldapserver
