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

from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.types import String, TIMESTAMP, Integer, Enum
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.helpers.db_manager import Base


class StatCallOnQueue(Base):

    __tablename__ = 'stat_call_on_queue'
    __table_args__ = (
        Index('stat_call_on_queue__idx_callid', 'callid'),
    )

    id = Column(Integer, primary_key=True)
    callid = Column(String(32), nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    ringtime = Column(Integer, nullable=False, server_default='0')
    talktime = Column(Integer, nullable=False, server_default='0')
    waittime = Column(Integer, nullable=False, server_default='0')
    status = Column(Enum('full',
                         'closed',
                         'joinempty',
                         'leaveempty',
                         'divert_ca_ratio',
                         'divert_waittime',
                         'answered',
                         'abandoned',
                         'timeout',
                         name='call_exit_type',
                         metadata=Base.metadata),
                    nullable=False)
    queue_id = Column(Integer, ForeignKey("stat_queue.id"))
    agent_id = Column(Integer, ForeignKey("stat_agent.id"))

    stat_queue = relationship(StatQueue, foreign_keys=queue_id)
    stat_agent = relationship(StatAgent, foreign_keys=agent_id)
