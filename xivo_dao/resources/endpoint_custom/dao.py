# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.resources.endpoint_custom.persistor import CustomPersistor


def persistor():
    return CustomPersistor(Session)


def get(id):
    return persistor().get(id)


def find_by(**criteria):
    return persistor().find_by(criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(criteria)


def search(**parameters):
    return persistor().search(parameters)


def create(custom):
    with flush_session(Session):
        return persistor().create(custom)


def edit(custom):
    with flush_session(Session):
        return persistor().edit(custom)


def delete(custom):
    with flush_session(Session):
        return persistor().delete(custom)
