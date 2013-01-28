# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao import stat_queue_dao, stat_agent_dao
from sqlalchemy import func, between, literal
from xivo_dao.helpers.db_manager import DbSession


def _add_call(callid, time, queue_name, event, waittime=None, agent=None, talktime=None):
    queue_id = int(stat_queue_dao.id_from_name(queue_name))
    call_on_queue = StatCallOnQueue()
    call_on_queue.time = time
    call_on_queue.callid = callid
    call_on_queue.queue_id = queue_id
    call_on_queue.status = event
    if agent:
        agent_id = stat_agent_dao.id_from_name(agent)
        call_on_queue.agent_id = agent_id
    if waittime:
        call_on_queue.waittime = waittime
    if talktime:
        call_on_queue.talktime = talktime

    DbSession().add(call_on_queue)
    DbSession().commit()


def add_abandoned_call(callid, time, queue_name, waittime):
    _add_call(callid, time, queue_name, 'abandoned', waittime)


def add_answered_call(callid, time, queue_name, agent, waittime, talktime):
    _add_call(callid, time, queue_name, 'answered', waittime, agent, talktime)


def add_full_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'full')


def add_joinempty_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'joinempty')


def add_leaveempty_call(callid, time, queue_name, waittime):
    _add_call(callid, time, queue_name, 'leaveempty', waittime)


def add_closed_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'closed')


def add_timeout_call(callid, time, queue_name, waittime):
    _add_call(callid, time, queue_name, 'timeout', waittime)


def get_periodic_stats(start, end):
    stats = {}

    rows = (DbSession()
            .query(func.date_trunc(literal('hour'), StatCallOnQueue.time),
                   StatCallOnQueue.queue_id,
                   StatCallOnQueue.status,
                   func.count(StatCallOnQueue.status))
            .group_by(func.date_trunc(literal('hour'), StatCallOnQueue.time),
                      StatCallOnQueue.queue_id,
                      StatCallOnQueue.status)
            .filter(between(StatCallOnQueue.time, start, end)))

    for period, queue_id, status, number in rows.all():
        if period not in stats:
            stats[period] = {}
        if queue_id not in stats[period]:
            stats[period][queue_id] = {'total': 0}
        stats[period][queue_id][status] = number
        stats[period][queue_id]['total'] += number

    return stats


def clean_table():
    DbSession().query(StatCallOnQueue).delete()
    DbSession().commit()


def remove_after(date):
    DbSession().query(StatCallOnQueue).filter(StatCallOnQueue.time >= date).delete()
    DbSession().commit()
