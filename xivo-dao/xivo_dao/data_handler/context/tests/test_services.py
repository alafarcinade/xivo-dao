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
from hamcrest import all_of, assert_that, equal_to, has_property

from xivo_dao.data_handler.context import services as context_services
from xivo_dao.data_handler.context.services import ContextRange

from xivo_dao.data_handler.context.model import Context, ContextType
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.exception import MissingParametersError, InvalidParametersError, \
    ElementAlreadyExistsError


class TestContext(unittest.TestCase):

    @patch('xivo_dao.context_dao.get')
    def test_find_by_name_inexistant(self, context_dao_get):
        context_name = 'inexistant_context'
        context_dao_get.return_value = None

        result = context_services.find_by_name(context_name)

        assert_that(result, equal_to(None))

    @patch('xivo_dao.context_dao.get')
    def test_find_by_name(self, context_dao_get):
        context_name = 'my_context'
        context_mock = Mock()
        context_dao_get.return_value = context_mock

        result = context_services.find_by_name(context_name)

        assert_that(result, equal_to(context_mock))

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_no_parameters(self, context_dao_create):
        context = Context()

        self.assertRaises(MissingParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_missing_parameters(self, context_dao_create):
        context = Context(display_name='Test')

        self.assertRaises(MissingParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_empty_parameters(self, context_dao_create):
        context = Context(name='', display_name='', type='')

        self.assertRaises(InvalidParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_invalid_type(self, context_dao_create):
        context = Context(name='test', display_name='test', type='invalidtype')

        self.assertRaises(InvalidParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_context_already_exists(self, context_dao_create, find_by_name):
        context_name = 'test'

        existing_context = Mock(Context)
        existing_context.name = context_name

        find_by_name.return_value = existing_context

        context = Context(name=context_name,
                          display_name=context_name,
                          type=ContextType.internal)

        self.assertRaises(ElementAlreadyExistsError, context_services.create, context)

        find_by_name.assert_called_once_with(context_name)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create(self, context_dao_create, find_by_name):
        context_name = 'test'

        find_by_name.return_value = None

        context = Context(name=context_name,
                          display_name=context_name,
                          type=ContextType.internal)

        context_dao_create.return_value = context

        result = context_services.create(context)

        find_by_name.assert_called_once_with(context_name)
        context_dao_create.assert_called_once_with(context)

        assert_that(result, all_of(
            has_property('name', context_name),
            has_property('display_name', context_name),
            has_property('type', ContextType.internal)))

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_no_ranges(self, context_ranges):
        expected = False

        context_name = 'default'

        extension = Extension(exten='1000',
                              context=context_name)

        context_ranges.return_value = []

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(context_name)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_when_below_minimum(self, context_ranges):
        expected = False

        extension = Extension(exten='1000',
                              context='default')

        expected_ranges = [(2000, 3000)]
        context_ranges.return_value = expected_ranges

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_when_above_maximum(self, context_ranges):
        expected = False

        extension = Extension(exten='9999',
                              context='default')

        expected_ranges = [(2000, 3000)]
        context_ranges.return_value = expected_ranges

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_when_inside_of_range(self, context_ranges):
        expected = True

        extension = Extension(exten='1000',
                              context='default')

        expected_ranges = [(1000, 3000)]
        context_ranges.return_value = expected_ranges

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_when_inside_second_range(self, context_ranges):
        expected = True

        extension = Extension(exten='2000',
                              context='default')

        expected_ranges = [(1000, 1999),
                           (2000, 2999)]
        context_ranges.return_value = expected_ranges

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_when_ranges_overlap(self, context_ranges):
        expected = True

        extension = Extension(exten='1450',
                              context='default')

        expected_ranges = [(1400, 2000),
                           (1000, 1500)]
        context_ranges.return_value = expected_ranges

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_with_single_value_using_wrong_value(self, context_ranges):
        expected = False

        extension = Extension(exten='1450',
                              context='default')

        expected_ranges = [(1000, None)]
        context_ranges.return_value = expected_ranges

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_with_single_value_using_right_value(self, context_ranges):
        expected = True

        extension = Extension(exten='1000',
                              context='default')

        expected_ranges = [(1000, None)]
        context_ranges.return_value = expected_ranges

        result = context_services.is_extension_inside_range(extension)

        assert_that(result, equal_to(expected))
        context_ranges.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_inside_range_when_extension_is_alphanumeric(self, context_ranges):
        extension = Extension(exten='ABC123',
                              context='default')

        self.assertRaises(InvalidParametersError, context_services.is_extension_inside_range, extension)

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    def test_is_extension_in_specific_range_when_no_ranges(self, find_all_specific_context_ranges):
        extension = Extension(exten='1000',
                              context='default')

        find_all_specific_context_ranges.return_value = []

        result = context_services.is_extension_in_specific_range(extension, ContextRange.users)

        assert_that(result, equal_to(False))

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    def test_is_extension_in_specific_range_with_one_range(self, find_all_specific_context_ranges):
        extension = Extension(exten='1000',
                              context='default')

        find_all_specific_context_ranges.return_value = [(1000, 2000)]

        result = context_services.is_extension_in_specific_range(extension, ContextRange.users)

        assert_that(result, equal_to(True))

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    def test_is_extension_in_specific_range_with_two_ranges(self, find_all_specific_context_ranges):
        extension = Extension(exten='1501',
                              context='default')

        find_all_specific_context_ranges.return_value = [(1000, 1500),
                                                         (1501, 2000)]

        result = context_services.is_extension_in_specific_range(extension, ContextRange.users)

        assert_that(result, equal_to(True))

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    def test_is_extension_in_specific_range_when_outside_of_range(self, find_all_specific_context_ranges):
        extension = Extension(exten='2001',
                              context='default')

        find_all_specific_context_ranges.return_value = [(1000, 2000)]

        result = context_services.is_extension_in_specific_range(extension, ContextRange.users)

        assert_that(result, equal_to(False))

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    def test_is_extension_in_specific_range_with_overlapping_ranges(self, find_all_specific_context_ranges):
        extension = Extension(exten='1450',
                              context='default')

        find_all_specific_context_ranges.return_value = [(1000, 1500),
                                                         (1400, 2000)]

        result = context_services.is_extension_in_specific_range(extension, ContextRange.users)

        assert_that(result, equal_to(True))

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    def test_is_extension_in_specific_range_with_single_value_right_value(self, find_all_specific_context_ranges):
        extension = Extension(exten='1000',
                              context='default')

        find_all_specific_context_ranges.return_value = [(1000, None)]

        result = context_services.is_extension_in_specific_range(extension, ContextRange.users)

        assert_that(result, equal_to(True))

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    def test_is_extension_in_specific_range_with_single_value_wrong_value(self, find_all_specific_context_ranges):
        extension = Extension(exten='1001',
                              context='default')

        find_all_specific_context_ranges.return_value = [(1000, None)]

        result = context_services.is_extension_in_specific_range(extension, ContextRange.users)

        assert_that(result, equal_to(False))
