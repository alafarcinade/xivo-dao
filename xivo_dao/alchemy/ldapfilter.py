# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class LdapFilter(Base):

    __tablename__ = 'ldapfilter'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer)
    ldapserverid = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False, server_default='')
    user = Column(String(255))
    passwd = Column(String(255))
    basedn = Column(String(255), nullable=False, server_default='')
    filter = Column(String(255), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False, default='')
