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


from sqlalchemy.schema import Column, ForeignKey, CheckConstraint, \
    ForeignKeyConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.helpers.db_manager import Base


class FuncKeyDestUser(Base):

    __tablename__ = 'func_key_dest_user'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id=1'),
    )

    func_key_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('userfeatures.id'), primary_key=True)
    destination_type_id = Column(Integer, primary_key=True, server_default="1")

    func_key = relationship("FuncKey")
    userfeatures = relationship("UserFeatures")
