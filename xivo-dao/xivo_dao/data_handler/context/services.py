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

from xivo_dao import context_dao as old_context_dao
from xivo_dao.data_handler.exception import MissingParametersError, InvalidParametersError, \
    ElementAlreadyExistsError
from xivo_dao.data_handler.context.model import Context, ContextType
from xivo_dao.data_handler.context import dao as context_dao


class ContextRange(object):
    users = 'user'
    queues = 'queue'
    groups = 'group'
    conference_rooms = 'meetme'
    incalls = 'incall'


def find_by_name(context_name):
    return old_context_dao.get(context_name)


def create(context):
    _validate(context)
    created_context = context_dao.create(context)
    return created_context


def is_extension_inside_range(extension):
    exten = _validate_exten(extension)
    context_ranges = context_dao.find_all_context_ranges(extension.context)
    return _is_exten_in_ranges(exten, context_ranges)


def _validate_exten(extension):
    if not extension.exten.isdigit():
        raise InvalidParametersError(['Alphanumeric extensions are not supported'])
    return int(extension.exten)


def _is_exten_in_ranges(exten, context_ranges):
    for minimum, maximum in context_ranges:
        if not maximum and exten == minimum:
            return True
        elif minimum <= exten <= maximum:
            return True
    return False


def is_extension_in_specific_range(extension, context_range):
    exten = _validate_exten(extension)
    context_ranges = context_dao.find_all_specific_context_ranges(extension.context, context_range)
    return _is_exten_in_ranges(exten, context_ranges)


def _validate(context):
    _validate_missing(context)
    _validate_empty(context)
    _validate_context_type(context)
    _validate_exists_already(context)


def _validate_missing(context):
    missing = context.missing_parameters()
    if len(missing) > 0:
        raise MissingParametersError(missing)


def _validate_empty(context):
    empty = []
    for parameter in Context.MANDATORY:
        if getattr(context, parameter).strip() == '':
            empty.append(parameter)

    if len(empty) > 0:
        raise InvalidParametersError(empty)


def _validate_context_type(context):
    if context.type not in ContextType.all():
        raise InvalidParametersError(['type'])


def _validate_exists_already(context):
    existing_context = find_by_name(context.name)
    if existing_context:
        raise ElementAlreadyExistsError('context')
