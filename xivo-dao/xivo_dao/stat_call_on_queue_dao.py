# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy import dbconnection
from xivo_dao import stat_queue_dao
from sqlalchemy import func, between

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _add_call(callid, time, queue_name, event):
    queue_id = int(stat_queue_dao.id_from_name(queue_name))
    call_on_queue = StatCallOnQueue()
    call_on_queue.time = time
    call_on_queue.callid = callid
    call_on_queue.queue_id = queue_id
    call_on_queue.status = event

    _session().add(call_on_queue)
    _session().commit()


def add_answered_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'answered')


def add_full_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'full')


def add_closed_call(callid, time, queue_name):
    _add_call(callid, time, queue_name, 'closed')


def get_periodic_stats(start, end):
    stats = {}

    res = (_session().query(StatCallOnQueue.queue_id, StatCallOnQueue.status, func.count(StatCallOnQueue.status))
           .group_by(StatCallOnQueue.queue_id, StatCallOnQueue.status)
           .filter(between(StatCallOnQueue.time, start, end)))

    for queue_id, status, count in res:
        if queue_id not in stats:
            stats[queue_id] = {'total': 0}
        stats[queue_id][status] = count
        stats[queue_id]['total'] += count

    return stats


def clean_table():
    _session().query(StatCallOnQueue).delete()
    _session().commit()
