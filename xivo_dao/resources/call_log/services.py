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


from xivo_dao.helpers import errors
from xivo_dao.resources.call_log import dao


def find_all():
    return dao.find_all()


def find_all_in_period(start, end):
    _validate_datetimes(start, end)
    return dao.find_all_in_period(start, end)


def _validate_datetimes(start, end):
    missing_parameters = []
    if not start:
        missing_parameters.append('start_date')
    if not end:
        missing_parameters.append('end_date')

    if missing_parameters:
        raise errors.missing(*missing_parameters)
