#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.staticmeetme import StaticMeetme
from xivo_dao.alchemy import dbconnection

from sqlalchemy import func

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def all():
    return _session().query(MeetmeFeatures).all()


def get(meetme_id):
    res = _session().query(MeetmeFeatures).filter(MeetmeFeatures.id == int(meetme_id)).first()
    if not res:
        raise LookupError
    return res


def _get_by_number(number):
    return _session().query(MeetmeFeatures).filter(MeetmeFeatures.confno == number)[0]


def is_a_meetme(number):
    row = (_session()
           .query(func.count(MeetmeFeatures.confno).label('count'))
           .filter(MeetmeFeatures.confno == number)).first()
    return row.count != 0


def find_by_name(meetme_name):
    res = _session().query(MeetmeFeatures).filter(MeetmeFeatures.name == meetme_name)
    if res.count() == 0:
        return ''
    return res[0]


def find_by_confno(meetme_confno):
    res = _session().query(MeetmeFeatures).filter(MeetmeFeatures.confno == meetme_confno)
    if res.count() == 0:
        raise LookupError('No such conference room: %s', meetme_confno)
    return res[0].id


def get_name(meetme_id):
    return get(meetme_id).name


def has_pin(meetme_id):
    meetme = get(meetme_id)
    var_val = _session().query(StaticMeetme.var_val).filter(StaticMeetme.id == meetme.meetmeid)
    return _has_pin_from_var_val(var_val[0].var_val)


def _has_pin_from_var_val(var_val):
    try:
        _, pin = var_val.split(',', 1)
    except ValueError:
        return False
    else:
        return len(pin) > 0


def get_configs():
    res = (_session().query(MeetmeFeatures.name, MeetmeFeatures.confno, StaticMeetme.var_val, MeetmeFeatures.context)
           .filter(MeetmeFeatures.meetmeid == StaticMeetme.id))
    return [(r.name, r.confno, _has_pin_from_var_val(r.var_val), r.context) for r in res]


def get_config(meetme_id):
    res = (_session().query(MeetmeFeatures.name, MeetmeFeatures.confno, StaticMeetme.var_val, MeetmeFeatures.context)
           .filter(MeetmeFeatures.meetmeid == StaticMeetme.id)
           .filter(MeetmeFeatures.id == meetme_id))[0]
    return (res.name, res.confno, _has_pin_from_var_val(res.var_val), res.context)


def muted_on_join_by_number(number):
    return _get_by_number(number).user_initiallymuted == 1