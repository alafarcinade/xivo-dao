# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from mock import Mock
import unittest
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import contains
from hamcrest import contains_inanyorder
from hamcrest import has_length

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.utils.search import SearchConfig
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.helpers.exception import InputError

from xivo_dao.alchemy.userfeatures import UserFeatures


class TestSearchSystem(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.config = SearchConfig(table=UserFeatures,
                                   columns={'lastname': UserFeatures.lastname,
                                            'firstname': UserFeatures.firstname,
                                            'simultcalls': UserFeatures.simultcalls,
                                            'userfield': UserFeatures.userfield},
                                   default_sort='lastname')
        self.search = SearchSystem(self.config)

    def test_given_no_parameters_then_sorts_rows_using_default_sort_and_direction(self):
        last_user_row = self.add_user(lastname='Zintrabi')
        first_user_row = self.add_user(lastname='Abigale')

        rows, total = self.search.search(self.session)

        assert_that(total, equal_to(2))
        assert_that(rows, contains(first_user_row, last_user_row))

    def test_given_order_then_sorts_rows_using_order(self):
        last_user_row = self.add_user(firstname='Bob', lastname='Abigale')
        first_user_row = self.add_user(firstname='Alice', lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'order': 'firstname'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(first_user_row, last_user_row))

    def test_given_direction_then_sorts_rows_using_direction(self):
        first_user_row = self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'direction': 'desc'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(last_user_row, first_user_row))

    def test_given_limit_is_negative_number_then_raises_error(self):
        self.assertRaises(InputError,
                          self.search.search,
                          self.session, {'limit': -1})

    def test_given_limit_is_zero_then_raises_error(self):
        self.assertRaises(InputError,
                          self.search.search,
                          self.session, {'limit': 0})

    def test_given_offset_is_negative_number_then_raises_error(self):
        self.assertRaises(InputError,
                          self.search.search,
                          self.session, {'offset': -1})

    def test_given_limit_then_returns_same_number_of_rows_as_limit(self):
        self.add_user()
        self.add_user()

        rows, total = self.search.search(self.session, {'limit': 1})

        assert_that(total, equal_to(2))
        assert_that(rows, has_length(1))

    def test_given_offset_then_offsets_a_number_of_rows(self):
        self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'offset': 1})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(last_user_row))

    def test_given_offset_is_zero_then_does_not_offset_rows(self):
        first_user_row = self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'offset': 0})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(first_user_row, last_user_row))

    def test_given_skip_then_offset_a_number_of_rows(self):
        self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'skip': 1})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(last_user_row))

    def test_given_search_term_then_searches_in_columns_and_uses_default_sort(self):
        user_row1 = self.add_user(firstname='a123bcd', lastname='eeefghi')
        user_row2 = self.add_user(firstname='eeefghi', lastname='a123zzz')
        self.add_user(description='123')

        rows, total = self.search.search(self.session, {'search': '123'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(user_row2, user_row1))

    def test_given_search_term_then_searches_in_numeric_columns(self):
        self.add_user(simultcalls=1)
        user_row2 = self.add_user(simultcalls=2)

        rows, total = self.search.search(self.session, {'search': '2'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row2))

    def test_given_exact_match_numeric_term_in_param(self):
        self.add_user(firstname='Alice', lastname='First', simultcalls=3)
        user_row2 = self.add_user(firstname='Alice', lastname='Second', simultcalls=2)

        rows, total = self.search.search(self.session, {'search': 'ali', 'simultcalls': '2'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row2))

    def test_given_exact_match_userfield_term_in_param(self):
        self.add_user(firstname='Alice', lastname='First', userfield='mtl')
        user_row2 = self.add_user(firstname='Alice', lastname='Second', userfield='qc')

        rows, total = self.search.search(self.session, {'search': 'ali', 'userfield': 'qc'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row2))

    def test_given_no_search_with_params(self):
        self.add_user(firstname=u'Alïce', userfield='mtl')
        user_row2 = self.add_user(firstname=u'Bõb', userfield='qc')
        user_row3 = self.add_user(firstname=u'Çharles', userfield='qc')

        rows, total = self.search.search(self.session, {'userfield': 'qc'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(user_row2, user_row3))


class TestSearchConfig(unittest.TestCase):

    def test_given_list_of_sort_columns_then_returns_columns_for_sorting(self):
        table = Mock()
        column = Mock()
        column2 = Mock()
        config = SearchConfig(table=table,
                              columns={'column': column,
                                       'column2': column2,
                                       'column3': Mock()},
                              sort=['column', 'column2'],
                              default_sort='column')

        result = config.column_for_sorting('column2')

        assert_that(result, equal_to(column2))

    def test_given_no_columns_when_sorting_then_raises_error(self):
        table = Mock()

        config = SearchConfig(table=table, columns={}, default_sort='nothing')

        self.assertRaises(InputError, config.column_for_sorting, 'toto')

    def test_given_sort_column_does_not_exist_when_sorting_then_raises_error(self):
        table = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': 'column1'},
                              default_sort='column1')

        self.assertRaises(InputError, config.column_for_sorting, 'column2')

    def test_given_list_of_search_columns_then_returns_only_all_search_columns(self):
        table = Mock()
        column = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column, 'column2': Mock()},
                              search=['column1'],
                              default_sort='column1')

        result = config.all_search_columns()

        assert_that(result, contains(column))

    def test_given_list_of_columns_then_returns_all_all_search_columns(self):
        table = Mock()
        column1 = Mock()
        column2 = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column1, 'column2': column2},
                              default_sort='column1')

        result = config.all_search_columns()

        assert_that(result, contains_inanyorder(column1, column2))

    def test_that_column_for_searching_results_the_column(self):
        table = Mock()
        column1 = Mock()
        column2 = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column1, 'column2': column2},
                              default_sort='column1')

        result = config.column_for_searching('column1')

        assert_that(result, equal_to(column1))

    def test_that_column_for_searching_results_the_column_or_none(self):
        table = Mock()
        column1 = Mock()
        column2 = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column1, 'column2': column2},
                              default_sort='column1')

        result = config.column_for_searching('column3')

        assert_that(result, equal_to(None))
