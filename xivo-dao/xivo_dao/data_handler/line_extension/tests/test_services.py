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

import unittest
from mock import Mock, patch
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension import services as line_extension_service


class TestLineExtensionService(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.notifier.associated')
    @patch('xivo_dao.data_handler.line_extension.dao.associate')
    @patch('xivo_dao.data_handler.line_extension.validator.validate_associate')
    def test_associate(self,
                       validate_associate,
                       dao_associate,
                       notifier_associated):

        line_extension = Mock(LineExtension)
        created_line_extension = dao_associate.return_value = Mock(LineExtension)

        result = line_extension_service.associate(line_extension)

        assert_that(result, equal_to(created_line_extension))
        validate_associate.assert_called_once_with(line_extension)
        dao_associate.assert_called_once_with(line_extension)
        notifier_associated.assert_called_once_with(created_line_extension)
