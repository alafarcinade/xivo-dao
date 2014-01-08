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

from sqlalchemy.schema import Column, Sequence
from sqlalchemy.types import Integer, String, Text
from xivo_dao.helpers.db_manager import Base


class CtiDisplays(Base):

    __tablename__ = 'ctidisplays'

    id = Column(Integer, Sequence('ctidisplays_id_seq'), primary_key=True)
    name = Column(String(50))
    data = Column(Text, nullable=False)
    description = Column(Text)
    deletable = Column(Integer)
