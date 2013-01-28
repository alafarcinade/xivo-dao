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

from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.helpers.db_manager import DbSession

TRUNK_TYPES = ['sip', 'iax', 'custom']


def find_by_proto_name(protocol, name):
    if not protocol or protocol not in TRUNK_TYPES:
        raise ValueError('Protocol %s is not allowed', protocol)

    protocol = protocol.lower()
    table, field = _trunk_table_lookup_field(protocol)

    try:
        protocol_id = (DbSession().query(table.id)
                       .filter(field.ilike(name)))[0].id
        trunk_id = (DbSession().query(TrunkFeatures.id)
                    .filter(TrunkFeatures.protocolid == protocol_id)
                    .filter(TrunkFeatures.protocol == protocol.lower()))[0].id
    except IndexError:
        raise LookupError('No such trunk')
    else:
        return trunk_id


def _trunk_table_lookup_field(protocol):
    if protocol == 'sip':
        table = UserSIP
        field = UserSIP.name
    elif protocol == 'iax':
        table = UserIAX
        field = UserIAX.name
    elif protocol == 'custom':
        table = UserCustom
        field = UserCustom.interface
    return table, field


def get_ids():
    return [item.id for item in DbSession().query(TrunkFeatures.id)]


def get(trunk_id):
    return DbSession().query(TrunkFeatures).filter(TrunkFeatures.id == trunk_id).first()


def all():
    return DbSession().query(TrunkFeatures).all()
