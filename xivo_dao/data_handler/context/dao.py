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

from xivo_dao.alchemy.context import Context as ContextSchema
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.contextnumbers import ContextNumbers as ContextNumberSchema
from xivo_dao.alchemy.entity import Entity as EntitySchema
from xivo_dao.data_handler.context.model import db_converter
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.helpers.db_manager import daosession, xivo_daosession


@daosession
def get(session, context_name):
    context_row = (session.query(ContextSchema)
                   .filter(ContextSchema.name == context_name)
                   .first())

    if not context_row:
        raise ElementNotExistsError('Context', name=context_name)

    return db_converter.to_model(context_row)


@daosession
def get_by_extension_id(session, extension_id):
    context_row = (session.query(ContextSchema)
                   .join(ExtensionSchema, ExtensionSchema.context == ContextSchema.name)
                   .filter(ExtensionSchema.id == extension_id)
                   .first())

    if not context_row:
        raise ElementNotExistsError('Context', extension_id=extension_id)

    return db_converter.to_model(context_row)


@daosession
def create(session, context):
    context_row = db_converter.to_source(context)
    context_row.entity = _get_default_entity_name()

    session.begin()
    session.add(context_row)
    session.commit()

    return context


@xivo_daosession
def _get_default_entity_name(session):
    entity = session.query(EntitySchema).first()
    return entity.name


@daosession
def find_all_context_ranges(session, context_name):
    rows = (session.query(
        ContextNumberSchema.numberbeg,
        ContextNumberSchema.numberend)
        .filter(ContextNumberSchema.context == context_name)
        .all())

    ranges = []

    for row in rows:
        minimum, maximum = _convert_minimum_maximum(row)
        ranges.append((minimum, maximum))

    return ranges


@daosession
def find_all_specific_context_ranges(session, context_name, context_range):
    rows = (session.query(
        ContextNumberSchema.numberbeg,
        ContextNumberSchema.numberend)
        .filter(ContextNumberSchema.context == context_name)
        .filter(ContextNumberSchema.type == context_range)
        .all())

    ranges = []

    for row in rows:
        minimum, maximum = _convert_minimum_maximum(row)
        ranges.append((minimum, maximum))

    return ranges


def _convert_minimum_maximum(row):
    minimum = int(row.numberbeg)
    if row.numberend:
        maximum = int(row.numberend)
    else:
        maximum = None

    return minimum, maximum
