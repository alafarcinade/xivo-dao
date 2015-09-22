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

from sqlalchemy.sql.expression import and_, or_

from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.entity import dao as entity_dao

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import DataError
from xivo_dao.resources.user.search import user_search
from xivo_dao.resources.user.view import user_view
from xivo_dao.resources.user.database import db_converter
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.db_utils import commit_or_abort


DEFAULT_ORDER = [UserSchema.lastname, UserSchema.firstname]


@daosession
def search(session, **parameters):
    view = user_view.select(parameters.get('view'))
    query = view.query(session)
    rows, total = user_search.search_from_query(query, parameters)
    users = view.convert_list(rows)
    return SearchResult(total, users)


@daosession
def find_all(session, order=None):
    user_rows = _user_query(session, order).all()

    return _rows_to_user_model(user_rows)


@daosession
def find_all_by_fullname(session, fullname, order=None):
    fullname_column = UserSchema.firstname + " " + UserSchema.lastname
    search = '%%%s%%' % fullname.lower()

    user_rows = (_user_query(session, order)
                 .filter(fullname_column.ilike(search))
                 .all())

    return _rows_to_user_model(user_rows)


def _user_query(session, order=None):
    order = order or DEFAULT_ORDER
    return session.query(UserSchema).order_by(*order)


def _rows_to_user_model(user_rows):
    if not user_rows:
        return []

    users = []
    for user_row in user_rows:
        user_model = db_converter.to_model(user_row)
        users.append(user_model)

    return users


@daosession
def find_user(session, firstname, lastname):
    user_row = (session.query(UserSchema)
                .filter(UserSchema.firstname == firstname)
                .filter(UserSchema.lastname == lastname)
                .first())
    if not user_row:
        return None

    return db_converter.to_model(user_row)


@daosession
def get(session, user_id):
    user_row = _fetch_commented_user_row(session, user_id)
    return db_converter.to_model(user_row)


@daosession
def get_by_uuid(session, user_uuid):
    query = session.query(UserSchema).filter(UserSchema.uuid == str(user_uuid))
    user_row = _user_row_from_query(query, user_uuid)
    return db_converter.to_model(user_row)


def _fetch_commented_user_row(session, user_id):
    query = session.query(UserSchema).filter(UserSchema.id == user_id)
    return _user_row_from_query(query, user_id)


def _user_row_from_query(query, user_id):
    user_row = query.first()
    if not user_row:
        raise errors.not_found('User', id=user_id)
    return user_row


@daosession
def get_main_user_by_line_id(session, line_id):
    row = (session.query(UserSchema, UserLineSchema)
           .filter(UserLineSchema.user_id == UserSchema.id)
           .filter(UserLineSchema.line_id == line_id)
           .filter(UserLineSchema.main_user == True)
           .first())

    if not row:
        raise errors.not_found('User', line_id=line_id)

    user_row, _ = row
    return db_converter.to_model(user_row)


@daosession
def find_by_number_context(session, number, context):
    return _find_by_number_context(session, number, context)


def _find_by_number_context(session, number, context):
    user_row = (session.query(UserSchema)
                .join(ExtensionSchema, and_(ExtensionSchema.context == context,
                                            ExtensionSchema.exten == number,
                                            ExtensionSchema.commented == 0))
                .join(LineSchema, and_(LineSchema.commented == 0))
                .join(UserLineSchema, and_(UserLineSchema.user_id == UserSchema.id,
                                           UserLineSchema.extension_id == ExtensionSchema.id,
                                           UserLineSchema.line_id == LineSchema.id,
                                           UserLineSchema.main_line == True))
                .first())

    if not user_row:
        return None

    return db_converter.to_model(user_row)


@daosession
def get_by_number_context(session, number, context):
    user = _find_by_number_context(session, number, context)
    if not user:
        raise errors.not_found('User', number=number, context=context)
    return user


@daosession
def find_all_by_template_id(session, template_id, private=True):
    if private:
        criteria = or_(UserSchema.func_key_template_id == template_id,
                       UserSchema.func_key_private_template_id == template_id)
    else:
        criteria = (UserSchema.func_key_template_id == template_id)

    query = session.query(UserSchema).filter(criteria)
    return [db_converter.to_model(row) for row in query]


@daosession
def create(session, user):
    user_row = db_converter.to_source(user)
    user_row.entityid = entity_dao.default_entity_id()

    with commit_or_abort(session, DataError.on_create, 'User'):
        session.add(user_row)

    user.uuid = user_row.uuid
    user.id = user_row.id
    user.caller_id = user_row.callerid

    return user


@daosession
def edit(session, user):
    user_row = _fetch_commented_user_row(session, user.id)

    db_converter.update_source(user_row, user)

    with commit_or_abort(session, DataError.on_edit, 'User'):
        session.add(user_row)


@daosession
def delete(session, user):
    with commit_or_abort(session, DataError.on_delete, 'User'):
        _delete_user(session, user.id)


def _delete_user(session, user_id):
    result = (session.query(UserSchema).filter(UserSchema.id == user_id).delete())
    (session.query(QueueMember).filter(QueueMember.usertype == 'user')
                               .filter(QueueMember.userid == user_id)
                               .delete())
    (session.query(RightCallMember).filter(RightCallMember.type == 'user')
                                   .filter(RightCallMember.typeval == str(user_id))
                                   .delete())
    (session.query(Callfiltermember).filter(Callfiltermember.type == 'user')
                                    .filter(Callfiltermember.typeval == str(user_id))
                                    .delete())
    (session.query(Dialaction).filter(Dialaction.category == 'user')
                              .filter(Dialaction.categoryval == str(user_id))
                              .delete())
    (session.query(PhoneFunckey).filter(PhoneFunckey.iduserfeatures == user_id).delete())
    (session.query(SchedulePath).filter(SchedulePath.path == 'user')
                                .filter(SchedulePath.pathid == user_id)
                                .delete())
    return result


@daosession
def is_cti_enabled(session, userid):
    enableclient = session.query(UserSchema).filter(UserSchema.id == userid).first().enableclient
    return enableclient == 1
