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

from xivo_dao.alchemy.context import Context as ContextSchema
from xivo_dao.alchemy.entity import Entity as EntitySchema

from xivo_dao.data_handler.context.model import Context, ContextType
from xivo_dao.data_handler.context import dao as context_dao
from hamcrest import *


class TestContextDao(DAOTestCase):

    tables = [
        ContextSchema,
        EntitySchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_create(self):
        entity_name = 'testentity'
        context_name = 'contextname'
        context_type = ContextType.internal

        context = Context(name=context_name,
                          display_name=context_name,
                          type=context_type)

        self._insert_entity(entity_name)

        context_dao.create(context)

        context_row = self.session.query(ContextSchema).filter(ContextSchema.name == context_name).first()

        assert_that(context_row, all_of(
            has_property('name', context_name),
            has_property('displayname', context_name),
            has_property('entity', entity_name),
            has_property('contexttype', context_type),
            has_property('commented', 0),
            has_property('description', '')
        ))

    def _insert_entity(self, entity_name):
        entity = EntitySchema(name=entity_name,
                              displayname=entity_name)

        self.session.begin()
        self.session.add(entity)
        self.session.commit()

        return entity