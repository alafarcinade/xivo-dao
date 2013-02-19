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

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Enum, Text
from xivo_dao.helpers.db_manager import Base, Type


class Callfilter(Base):

    __tablename__ = 'callfilter'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, server_default='')
    context = Column(String(39), nullable=False)
    type = Column(Enum('bosssecretary',
                       name='callfilter_type',
                       metadata=Type.metadata),
                  nullable=False)
    bosssecretary = Column(Enum('bossfirst-serial', 'bossfirst-simult', 'secretary-serial', 'secretary-simult', 'all',
                               name='callfilter_bosssecretary',
                               metadata=Type.metadata),
                          nullable=False)
    callfrom = Column(Enum('internal', 'external', 'all',
                           name='callfilter_callfrom',
                           metadata=Type.metadata),
                      nullable=False)
    ringseconds = Column(Integer, nullable=False, default=0)
    commented = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=False)
