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

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.cti_profile import CtiProfile as CtiProfileSchema
from hamcrest.library.object.haslength import has_length
from hamcrest.core import assert_that
from xivo_dao.data_handler.cti_profile import dao
from hamcrest.core.core.isequal import equal_to
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup

class TestCtiProfile(DAOTestCase):
    tables = [CtiProfileSchema, CtiPresences, CtiPhoneHintsGroup]

    def setUp(self):
        self.empty_tables()

    def test_find_all(self):
        profile_row1 = CtiProfileSchema(id=1, name='Profil 01')
        profile_row2 = CtiProfileSchema(id=2, name='Profil 02')
        self.add_me(profile_row1)
        self.add_me(profile_row2)

        result = dao.find_all()

        assert_that(result, has_length(2))
        assert_that(result[0].id, equal_to(1))
        assert_that(result[0].name, equal_to('Profil 01'))
        assert_that(result[1].id, equal_to(2))
        assert_that(result[1].name, equal_to('Profil 02'))
