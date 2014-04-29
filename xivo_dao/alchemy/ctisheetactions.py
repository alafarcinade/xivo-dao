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
from sqlalchemy.types import Integer, String, Text

from xivo_dao.helpers.db_manager import Base


class CtiSheetActions(Base):

    __tablename__ = 'ctisheetactions'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(Text, nullable=False)
    whom = Column(String(50))
    sheet_info = Column(Text)
    systray_info = Column(Text)
    sheet_qtui = Column(Text)
    action_info = Column(Text)
    focus = Column(Integer)
    deletable = Column(Integer)
    disable = Column(Integer)
