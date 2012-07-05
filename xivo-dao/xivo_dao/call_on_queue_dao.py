# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.call_on_queue import CallOnQueue
from xivo_dao.alchemy import dbconnection
from xivo_dao import queue_features_dao

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def add_full_call(callid, time, queue_name):
    queue_id = int(queue_features_dao.id_from_name(queue_name))
    call_on_queue = CallOnQueue()
    call_on_queue.time = time
    call_on_queue.callid = callid
    call_on_queue.queue_id = queue_id
    call_on_queue.status = 'full'

    _session().add(call_on_queue)
    _session().commit()
