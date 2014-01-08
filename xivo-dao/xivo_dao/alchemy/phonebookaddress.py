# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from sqlalchemy.types import Integer, String, Enum
from xivo_dao.helpers.db_manager import Base, Type


class PhonebookAddress(Base):

    __tablename__ = 'phonebookaddress'

    id = Column(Integer, primary_key=True)
    phonebookid = Column(Integer, nullable=False)
    address1 = Column(String(30), nullable=False, default='')
    address2 = Column(String(30), nullable=False, default='')
    city = Column(String(128), nullable=False, default='')
    state = Column(String(128), nullable=False, default='')
    zipcode = Column(String(16), nullable=False, default='')
    country = Column(String(3), nullable=False, default='')
    type = Column(Enum(('home', 'office', 'other'), name='phonebookaddress_type', metadata=Type.metadata),
                  nullable=False)
