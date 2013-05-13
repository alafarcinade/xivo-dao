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

from sqlalchemy.schema import Column, Sequence
from sqlalchemy.types import Integer, String
from xivo_dao.helpers.db_manager import Base


class CtiSheetEvents(Base):

    __tablename__ = 'ctisheetevents'

    id = Column(Integer, Sequence('ctisheetevents_id_seq'), primary_key=True)
    incomingdid = Column(String(50))
    hangup = Column(String(50))
    dial = Column(String(50))
    link = Column(String(50))
    unlink = Column(String(50))
