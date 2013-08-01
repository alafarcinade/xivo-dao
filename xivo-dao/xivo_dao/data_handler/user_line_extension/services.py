# -*- coding: utf-8 -*-
#
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

import dao
import notifier

from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementNotExistsError
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.extension import services as extension_services


def get(ule_id):
    return dao.get(ule_id)


def find_all():
    return dao.find_all()


def find_all_by_user_id(user_id):
    return dao.find_all_by_user_id(user_id)


def find_all_by_extension_id(extension_id):
    return dao.find_all_by_extension_id(extension_id)


def create(ule):
    _validate(ule)
    extension = dao.create(ule)
    notifier.created(ule)
    return extension


def edit(ule):
    _validate(ule)
    dao.edit(ule)
    notifier.edited(ule)


def delete(ule):
    dao.delete(ule)
    _remove_user(ule)
    _remove_line(ule)
    _remove_exten(ule)
    notifier.deleted(ule)


def _validate(ule):
    _check_missing_parameters(ule)
    _check_invalid_parameters(ule)


def _check_missing_parameters(ule):
    missing = ule.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(ule_id):
    invalid_parameters = []
    if not isinstance(ule_id.user_id, int):
        invalid_parameters.append('user_id must be integer')
    if ule_id.user_id == 0:
        invalid_parameters.append('user_id equal to 0')
    if not isinstance(ule_id.line_id, int):
        invalid_parameters.append('line_id must be integer')
    if ule_id.line_id == 0:
        invalid_parameters.append('line_id equal to 0')
    if not isinstance(ule_id.extension_id, int):
        invalid_parameters.append('extension_id must be integer')
    if ule_id.extension_id == 0:
        invalid_parameters.append('extension_id equal to 0')
    if not isinstance(ule_id.main_line, bool):
        invalid_parameters.append('main_line must be boolean')
    if not isinstance(ule_id.main_user, bool):
        invalid_parameters.append('main_user must be boolean')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _remove_user(ule):
    try:
        user = user_services.get(ule.user_id)
        user_services.delete(user)
    except ElementNotExistsError:
        return


def _remove_line(ule):
    try:
        line = line_services.get(ule.line_id)
        line_services.delete(line)
    except ElementNotExistsError:
        return


def _remove_exten(ule):
    try:
        extension = extension_services.get(ule.extension_id)
        extension_services.delete(extension)
    except ElementNotExistsError:
        return
