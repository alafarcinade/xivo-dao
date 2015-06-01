# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.queue import dao as queue_dao


class TestQueueExist(DAOTestCase):

    def test_given_no_queue_then_returns_false(self):
        result = queue_dao.exists(1)

        assert_that(result, equal_to(False))

    def test_given_queue_exists_then_return_true(self):
        queue_row = self.add_queuefeatures()

        result = queue_dao.exists(queue_row.id)

        assert_that(result, equal_to(True))
