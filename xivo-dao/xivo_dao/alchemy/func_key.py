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


from xivo_dao.helpers.db_manager import Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship
from xivo_dao.alchemy.func_key_type import FuncKeyType
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser

test_dependencies = [
    FuncKeyType,
    FuncKeyDestinationType,
    FuncKeyDestUser,
]


class FuncKey(Base):

    __tablename__ = 'func_key'

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('func_key_type.id'), nullable=False)
    destination_type_id = Column(Integer, ForeignKey('func_key_destination_type.id'), nullable=False)

    func_key_type = relationship("FuncKeyType")
    destination_type = relationship("FuncKeyDestinationType")
