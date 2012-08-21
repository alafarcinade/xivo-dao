# -*- coding: UTF-8 -*-

import datetime
import re

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog
from sqlalchemy import cast, TIMESTAMP


_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"
_TIME_STRING_PATTERN = re.compile('(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).?(\d+)?')
_MAP_QUEUE_LOG_WAITTIME = {'answered': QueueLog.data1,
                           'abandoned': QueueLog.data3,
                           'timeout': QueueLog.data3}
FIRST_EVENT = ['FULL', 'ENTERQUEUE', 'CLOSED', 'JOINEMPTY']
WAIT_TIME_EVENT = ['CONNECT', 'LEAVEEMPTY', 'EXITWITHTIMEOUT', 'ABANDON']


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get_event_with_enterqueue(start, end, match, event):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    enter_queues = (_session()
                    .query(QueueLog.callid,
                           cast(QueueLog.time, TIMESTAMP).label('time'))
                    .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                 between(QueueLog.time, start, end))))

    enter_map = {}
    for enter_queue in enter_queues:
        enter_map[enter_queue.callid] = enter_queue.time

    if match == 'CONNECT':
        match = ['CONNECT', 'COMPLETECALLER', 'COMPLETEAGENT', 'TRANSFER']
    else:
        match = [match]

    if not enter_map:
        return []

    res = (_session()
           .query(QueueLog.event,
                  QueueLog.queuename,
                  cast(QueueLog.time, TIMESTAMP).label('time'),
                  QueueLog.callid,
                  QueueLog.agent,
                  QueueLog.data1,
                  QueueLog.data2,
                  QueueLog.data3,
                  QueueLog.data4)
           .filter(and_(QueueLog.event.in_(match),
                        QueueLog.callid.in_(enter_map))))

    ret = {}
    for r in res:
        if r.callid not in ret:
            ret[r.callid] = {
                'callid': r.callid,
                'queue_name': r.queuename,
                'time': enter_map[r.callid],
                'event': event,
                'talktime': 0
                }
        if r.agent:
            ret[r.callid]['agent'] = r.agent
        if r.event in WAIT_TIME_EVENT:
            if r.event == 'LEAVEEMPTY':
                waittime = _time_diff(enter_map[r.callid], r.time)
                ret[r.callid]['waittime'] = waittime
            elif r.event == 'CONNECT':
                ret[r.callid]['waittime'] = int(r.data1)
            else:
                ret[r.callid]['waittime'] = int(r.data3)
        elif r.event in ['COMPLETECALLER', 'COMPLETEAGENT']:
            ret[r.callid]['talktime'] = int(r.data2)
        elif r.event == 'TRANSFER':
            ret[r.callid]['talktime'] = int(r.data4)

    return ret.values()


def get_queue_abandoned_call(start, end):
    return _get_event_with_enterqueue(start, end, 'ABANDON', 'abandoned')


def get_queue_timeout_call(start, end):
    return _get_event_with_enterqueue(start, end, 'EXITWITHTIMEOUT', 'timeout')


def get_queue_leaveempty_call(start, end):
    return _get_event_with_enterqueue(start, end, 'LEAVEEMPTY', 'leaveempty')


def _time_diff(start, end):
    delta = end - start
    return delta.seconds + int(round(delta.microseconds / 1000000.0))


def get_enterqueue_time(callids):
    return dict([(r.callid, r.time)
                 for r in (_session()
                           .query(QueueLog.callid,
                                  cast(QueueLog.time, TIMESTAMP).label('time'))
                           .filter(and_(QueueLog.event == 'ENTERQUEUE',
                                        QueueLog.callid.in_(callids))))])


def _time_str_to_datetime(s):
    if not s:
        raise LookupError
    m = _TIME_STRING_PATTERN.match(s)
    return datetime.datetime(int(m.group(1)),
                             int(m.group(2)),
                             int(m.group(3)),
                             int(m.group(4)),
                             int(m.group(5)),
                             int(m.group(6)),
                             int(m.group(7)) if m.group(7) else 0)


def get_first_time():
    return _session().query(cast(min(QueueLog.time), TIMESTAMP))[0][0]


def get_queue_names_in_range(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    return [r[0] for r in (_session().query(distinct(QueueLog.queuename))
                                  .filter(between(QueueLog.time, start, end)))]


def get_agents_after(start):
    s = start.strftime(_STR_TIME_FMT)

    return [r.agent for r in (_session()
                              .query(distinct(QueueLog.agent).label('agent'))
                              .filter(QueueLog.time >= s))]


def delete_event_by_queue_between(event, qname, start, end):
    _session().query(QueueLog).filter(
        and_(QueueLog.event == event,
             QueueLog.queuename == qname,
             between(QueueLog.time, start, end))).delete(synchronize_session=False)
    _session().commit()


def insert_entry(time, callid, queue, agent, event, d1='', d2='', d3='', d4='', d5=''):
    entry = QueueLog(
        time=time,
        callid=callid,
        queuename=queue,
        agent=agent,
        event=event,
        data1=d1,
        data2=d2,
        data3=d3,
        data4=d4,
        data5=d5)
    _session().add(entry)
    _session().commit()
