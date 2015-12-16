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

from sqlalchemy.sql.expression import or_

from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.helpers import errors
from xivo_dao.resources.extension.database import db_converter, \
    fwd_converter, service_converter, agent_action_converter
from xivo_dao.resources.extension.search import extension_search
from xivo_dao.resources.extension.fixes import ExtensionFixes
from xivo_dao.resources.utils.search import SearchResult

DEFAULT_ORDER = ExtensionSchema.exten


def find_query(session, criteria):
    query = session.query(ExtensionSchema)
    for name, value in criteria.iteritems():
        column = getattr(ExtensionSchema, name, None)
        if not column:
            raise errors.unknown(column)
        query = query.filter(column == value)
    return query


@daosession
def find_by(session, **criteria):
    query = find_query(session, criteria)
    row = query.first()
    return db_converter.to_model(row) if row else None


def get_by(**criteria):
    extension = find_by(**criteria)
    if not extension:
        raise errors.not_found('Extension', **criteria)
    return extension


@daosession
def find_all_by(session, **criteria):
    query = find_query(session, criteria)
    return [db_converter.to_model(row) for row in query]


def get(extension_id):
    return get_by(id=extension_id)


@daosession
def get_by_exten_context(session, exten, context):
    return get_by(exten=exten, context=context)


@daosession
def find(session, extension_id):
    return find_by(id=extension_id)


@daosession
def search(session, **parameters):
    rows, total = extension_search.search(session, parameters)
    extensions = [db_converter.to_model(row) for row in rows]
    return SearchResult(total, extensions)


@daosession
def find_by_exten(session, exten, order=None):
    search = '%%%s%%' % exten.lower()
    return _find_all_by_search(session, search, order)


@daosession
def find_by_context(session, context, order=None):
    search = '%%%s%%' % context.lower()
    return _find_all_by_search(session, search, order)


@daosession
def find_by_exten_context(session, exten, context):
    return find_by(exten=exten, context=context)


def get_by_type(type_, typeval):
    return get_by(type=type_, typeval=str(typeval))


def get_by_group_id(group_id):
    return get_by_type('group', group_id)


def get_by_queue_id(queue_id):
    return get_by_type('queue', queue_id)


def get_by_conference_id(conference_id):
    return get_by_type('meetme', conference_id)


def _find_all_by_search(session, search, order):
    query = (_new_query(session, order)
             .filter(or_(ExtensionSchema.exten.ilike(search),
                         ExtensionSchema.context.ilike(search))))

    return [db_converter.to_model(row) for row in query]


@daosession
def create(session, extension):
    extension_row = db_converter.to_source(extension)
    extension_row.type = 'user'
    extension_row.typeval = '0'

    with flush_session(session):
        session.add(extension_row)

    extension.id = extension_row.id

    return extension


@daosession
def edit(session, extension):
    extension_row = find_query(session, {'id': extension.id}).one()
    db_converter.update_source(extension_row, extension)

    with flush_session(session):
        session.add(extension_row)
        session.flush()
        ExtensionFixes(session).fix(extension_row.id)


@daosession
def delete(session, extension):
    with flush_session(session):
        session.query(ExtensionSchema).filter(ExtensionSchema.id == extension.id).delete()


def _new_query(session, order=None):
    order = order or DEFAULT_ORDER
    return session.query(ExtensionSchema).order_by(order)


@daosession
def get_type_typeval(session, extension_id):
    row = (session.query(ExtensionSchema.type, ExtensionSchema.typeval)
           .filter(ExtensionSchema.id == extension_id)
           .first())

    if not row:
        raise errors.not_found('Extension', id=extension_id)

    return (row.type, row.typeval)


@daosession
def find_all_service_extensions(session):
    typevals = service_converter.typevals()
    query = (session.query(ExtensionSchema.id,
                           ExtensionSchema.exten,
                           ExtensionSchema.typeval)
             .filter(ExtensionSchema.type == 'extenfeatures')
             .filter(ExtensionSchema.typeval.in_(typevals))
             )

    return [service_converter.to_model(row) for row in query]


@daosession
def find_all_forward_extensions(session):
    typevals = fwd_converter.typevals()
    query = (session.query(ExtensionSchema.id,
                           ExtensionSchema.exten,
                           ExtensionSchema.typeval)
             .filter(ExtensionSchema.type == 'extenfeatures')
             .filter(ExtensionSchema.typeval.in_(typevals))
             )

    return [fwd_converter.to_model(row) for row in query]


@daosession
def find_all_agent_action_extensions(session):
    typevals = agent_action_converter.typevals()
    query = (session.query(ExtensionSchema.id,
                           ExtensionSchema.exten,
                           ExtensionSchema.typeval)
             .filter(ExtensionSchema.type == 'extenfeatures')
             .filter(ExtensionSchema.typeval.in_(typevals))
             )

    return [agent_action_converter.to_model(row) for row in query]
