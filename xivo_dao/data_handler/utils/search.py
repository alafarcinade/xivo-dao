# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from sqlalchemy import String
from sqlalchemy.sql.expression import desc, asc, or_, cast


class SearchFilter(object):

    def __init__(self, base_query, columns, default_column):
        self.base_query = base_query
        self.columns = columns
        self.default_column = default_column

    def search(self, parameters=None):
        parameters = parameters or {}

        search_query = self.search_for(self.base_query, parameters.get('search', None))
        sorted_query = self.sort(search_query,
                                 parameters.get('order', None),
                                 parameters.get('direction', 'asc'))
        paginated_query = self.paginate(sorted_query,
                                        parameters.get('limit', None),
                                        parameters.get('skip', None))
        return paginated_query.all(), search_query.count()

    def search_for(self, query, term=None):
        if term is None:
            return self.base_query

        criteria = []
        for column in self.columns:
            column_search = cast(column, String).ilike('%%%s%%' % term)
            criteria.append(column_search)

        return self.base_query.filter(or_(*criteria))

    def paginate(self, query, limit=None, skip=None):
        if skip is not None:
            query = query.offset(skip)

        if limit is not None:
            query = query.limit(limit)

        return query

    def sort(self, query, order=None, direction='asc'):
        if order is None:
            order = self.default_column

        if direction == 'desc':
            order_expression = desc(order)
        else:
            order_expression = asc(order)

        return query.order_by(order_expression)
