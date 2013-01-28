# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from sqlalchemy import and_
from xivo_dao.helpers.db_manager import DbSession


def _get_dest(user_id, fwd_type):
    destinations = (DbSession().query(PhoneFunckey.exten)
                    .filter(and_(PhoneFunckey.iduserfeatures == user_id,
                                 PhoneFunckey.typevalextenumbers == fwd_type)))

    destinations = [d.exten if d.exten else '' for d in destinations.all()]

    return destinations


def get_dest_unc(user_id):
    return _get_dest(user_id, 'fwdunc')


def get_dest_rna(user_id):
    return _get_dest(user_id, 'fwdrna')


def get_dest_busy(user_id):
    return _get_dest(user_id, 'fwdbusy')
