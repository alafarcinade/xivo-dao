# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint, CheckConstraint, \
    ForeignKeyConstraint
from sqlalchemy.types import Integer, Boolean, String
from sqlalchemy.orm import relationship

from xivo_dao.helpers.db_manager import Base


class FuncKeyMapping(Base):

    __tablename__ = 'func_key_mapping'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        UniqueConstraint('template_id', 'position'),
        CheckConstraint('position > 0')
    )

    template_id = Column(Integer, ForeignKey('func_key_template.id'), primary_key=True)
    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(Integer, primary_key=True)
    label = Column(String(128))
    position = Column(Integer, nullable=False)
    blf = Column(Boolean, nullable=False, server_default='True')

    func_key_template = relationship("FuncKeyTemplate")
    func_key = relationship("FuncKey")
