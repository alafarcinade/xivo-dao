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
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class UserCustom(Base):

    __tablename__ = 'usercustom'

    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    context = Column(String(39))
    interface = Column(String(128), nullable=False)
    intfsuffix = Column(String(32), nullable=False, server_default='')
    commented = Column(Integer, nullable=False, server_default='0')
    protocol = Column(String(8), nullable=False, server_default='custom')
    category = Column(String(8))
