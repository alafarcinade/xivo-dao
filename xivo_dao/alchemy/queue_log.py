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

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import String, Integer, Text

from xivo_dao.helpers.db_manager import Base


class QueueLog(Base):

    __tablename__ = 'queue_log'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('queue_log__idx_agent', 'agent'),
        Index('queue_log__idx_callid', 'callid'),
        Index('queue_log__idx_event', 'event'),
        Index('queue_log__idx_time', 'time'),
    )

    time = Column(String(26), nullable=False, server_default='')
    callid = Column(String(32), nullable=False, server_default='')
    queuename = Column(String(50), nullable=False, server_default='')
    agent = Column(String(50), nullable=False, server_default='')
    event = Column(String(20), nullable=False, server_default='')
    data1 = Column(Text, server_default='')
    data2 = Column(Text, server_default='')
    data3 = Column(Text, server_default='')
    data4 = Column(Text, server_default='')
    data5 = Column(Text, server_default='')
    id = Column(Integer)
