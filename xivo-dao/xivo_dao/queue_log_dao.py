# -*- coding: UTF-8 -*-
import datetime
import re

from sqlalchemy import between, distinct
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import min
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queue_log import QueueLog


_DB_NAME = 'asterisk'
_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"
_TIME_STRING_PATTERN = r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).?(\d+)?'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get_queue_event_call(start, end, event_filter, name):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)
    res = (_session()
           .query(QueueLog.queuename, QueueLog.time, QueueLog.callid)
           .filter(and_(QueueLog.event == event_filter,
                        between(QueueLog.time, start, end))))
    return [{'queue_name': r.queuename,
             'event': name,
             'time': r.time,
             'callid': r.callid} for r in res]


def get_queue_full_call(start, end):
    return _get_queue_event_call(start, end, 'FULL', 'full')


def get_queue_closed_call(start, end):
    return _get_queue_event_call(start, end, 'CLOSED', 'closed')


def get_queue_abandoned_call(start, end):
    return _get_queue_event_call(start, end, 'ABANDON', 'abandoned')


def get_queue_answered_call(start, end):
    return _get_queue_event_call(start, end, 'CONNECT', 'answered')


def _time_str_to_datetime(s):
    m = re.match(_TIME_STRING_PATTERN, s)
    return datetime.datetime(int(m.group(1)),
                             int(m.group(2)),
                             int(m.group(3)),
                             int(m.group(4)),
                             int(m.group(5)),
                             int(m.group(6)),
                             int(m.group(7)) if m.group(7) else 0)


def get_first_time():
    return _time_str_to_datetime(_session().query(min(QueueLog.time))[0][0])


def get_queue_names_in_range(start, end):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    return [r[0] for r in (_session().query(distinct(QueueLog.queuename))
                                  .filter(between(QueueLog.time, start, end)))]
