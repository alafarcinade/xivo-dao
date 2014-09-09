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

from xivo_dao.data_handler import errors
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.data_handler.line_extension.model import db_converter
from xivo_dao.data_handler.user_line_extension import dao as ule_dao
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession


@daosession
def associate(session, line_extension):
    with commit_or_abort(session):
        _associate_ule(session, line_extension)
    return line_extension


def _associate_ule(session, line_extension):
    count = (session.query(UserLineSchema)
             .filter(UserLineSchema.line_id == line_extension.line_id)
             .count())

    if count > 0:
        _update_ules(session, line_extension)
    else:
        _create_ule(session, line_extension)


def _update_ules(session, line_extension):
    (session.query(UserLineSchema)
     .filter(UserLineSchema.line_id == line_extension.line_id)
     .update({'extension_id': line_extension.extension_id}))


def _create_ule(session, line_extension):
    user_line_row = db_converter.to_source(line_extension)
    session.add(user_line_row)


@daosession
def find_all_by_line_id(session, line_id):
    query = (session.query(UserLineSchema.line_id,
                           UserLineSchema.extension_id)
             .filter(UserLineSchema.line_id == line_id)
             .filter(UserLineSchema.extension_id != None)
             .distinct())

    return [db_converter.to_model(row) for row in query]


def find_by_line_id(line_id):
    line_extensions = find_all_by_line_id(line_id)
    return line_extensions[0] if line_extensions else None


def get_by_line_id(line_id):
    line_extension = find_by_line_id(line_id)

    if line_extension is None:
        raise errors.not_found('LineExtension', line_id=line_id)

    return line_extension


@daosession
def find_by_extension_id(session, extension_id):
    user_line_row = (session.query(UserLineSchema)
                     .filter(UserLineSchema.extension_id == extension_id)
                     .first())

    if not user_line_row:
        return None

    return db_converter.to_model(user_line_row)


def get_by_extension_id(extension_id):
    line_extension = find_by_extension_id(extension_id)

    if line_extension is None:
        raise errors.not_found('LineExtension', extension_id=extension_id)

    return line_extension


@daosession
def dissociate(session, line_extension):
    with commit_or_abort(session):
        _dissociate_ule(session, line_extension)
        ule_dao.delete_association_if_necessary(session)


def _dissociate_ule(session, line_extension):
    (session.query(UserLineSchema)
     .filter(UserLineSchema.line_id == line_extension.line_id)
     .update({'extension_id': None}))
