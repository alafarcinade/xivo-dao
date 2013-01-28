# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.alchemy.contexttype import ContextType
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.helpers.db_manager import daosession

@daosession
def get(session, context_name):
    return session.query(Context).filter(Context.name == context_name).first()


@daosession
def get_join_elements(session, context_name):
    return (session.query(Context, ContextNumbers, ContextType, ContextInclude)
            .join((ContextNumbers, Context.name == ContextNumbers.context),
                  (ContextType, Context.contexttype == ContextType.name))
            .outerjoin((ContextInclude, Context.name == ContextInclude.context))
            .filter(Context.name == context_name)
            .first())


@daosession
def all(session):
    return (session.query(Context, ContextNumbers, ContextType, ContextInclude)
            .join((ContextNumbers, Context.name == ContextNumbers.context),
                  (ContextType, Context.contexttype == ContextType.name))
            .outerjoin((ContextInclude, Context.name == ContextInclude.context))
            .all())
