# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from hamcrest.core import assert_that
from hamcrest.core.core.isequal import equal_to
from xivo_dao.alchemy.ctimain import CtiMain

from xivo_dao.resources.configuration import dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestConfigurationDao(DAOTestCase):

    def test_is_live_reload_enabled(self):
        ctimain = CtiMain(live_reload_conf=0)
        self.add_me(ctimain)

        result = dao.is_live_reload_enabled()

        self.assertFalse(result)

        ctimain.live_reload_conf = 1
        self.add_me(ctimain)

        result = dao.is_live_reload_enabled()

        self.assertTrue(result)

    def test_set_live_reload_status(self):
        ctimain = CtiMain(live_reload_conf=0)
        self.add_me(ctimain)

        dao.set_live_reload_status({'enabled': True})

        assert_that(ctimain.live_reload_conf, equal_to(1))
