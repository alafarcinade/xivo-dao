# -*- coding: utf-8 -*-
#
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint, \
    CheckConstraint
from sqlalchemy.types import Integer, String, Text, Enum

from xivo_dao.helpers.db_manager import Base


class Netiface(Base):

    __tablename__ = 'netiface'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('ifname'),
        CheckConstraint('type=\'iface\'')
    )

    id = Column(Integer, nullable=False)
    ifname = Column(String(64), nullable=False, server_default='')
    hwtypeid = Column(Integer, nullable=False, server_default='65534')
    networktype = Column(Enum('data',
                              'voip',
                              name='netiface_networktype',
                              metadata=Base.metadata),
                         nullable=False)
    type = Column(String(64), nullable=False)
    family = Column(Enum('inet',
                         'inet6',
                         name='netiface_family',
                         metadata=Base.metadata),
                    nullable=False)
    method = Column(Enum('static',
                         'dhcp',
                         'manual',
                         name='netiface_method',
                         metadata=Base.metadata))
    address = Column(String(39))
    netmask = Column(String(39))
    broadcast = Column(String(15))
    gateway = Column(String(39))
    mtu = Column(Integer)
    vlanrawdevice = Column(String(64))
    vlanid = Column(Integer)
    options = Column(Text)
    disable = Column(Integer, nullable=False, server_default='0')
    dcreate = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
