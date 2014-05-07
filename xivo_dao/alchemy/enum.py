# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from sqlalchemy.types import Enum

from xivo_dao.helpers.db_manager import Base


dialaction_action = Enum(
    'none',
    'endcall:busy',
    'endcall:congestion',
    'endcall:hangup',
    'user',
    'group',
    'queue',
    'meetme',
    'voicemail',
    'trunk',
    'schedule',
    'voicemenu',
    'extension',
    'outcall',
    'application:callbackdisa',
    'application:disa',
    'application:directory',
    'application:faxtomail',
    'application:voicemailmain',
    'application:password',
    'sound',
    'custom',
    name='dialaction_action',
    metadata=Base.metadata
)

extenumbers_type = Enum(
    'extenfeatures',
    'featuremap',
    'generalfeatures',
    'group',
    'incall',
    'meetme',
    'outcall',
    'queue',
    'user',
    'voicemenu',
    name='extenumbers_type',
    metadata=Base.metadata
)

generic_bsfilter = Enum(
    'no',
    'boss',
    'secretary',
    name='generic_bsfilter',
    metadata=Base.metadata
)

netiface_type = Enum(
    'iface',
    name='netiface_type',
    metadata=Base.metadata
)

serverfeatures_type = Enum(
    'xivo',
    'ldap',
    name='serverfeatures_type',
    metadata=Base.metadata
)

schedule_path_type = Enum(
    'user',
    'group',
    'queue',
    'incall',
    'outcall',
    'voicemenu',
    name='schedule_path_type',
    metadata=Base.metadata
)

trunk_protocol = Enum(
    'sip',
    'iax',
    'sccp',
    'custom',
    name='trunk_protocol',
    metadata=Base.metadata
)

useriax_protocol = Enum(
    'iax',
    name='useriax_protocol',
    metadata=Base.metadata
)

usersip_protocol = Enum(
    'sip',
    name='usersip_protocol',
    metadata=Base.metadata
)
