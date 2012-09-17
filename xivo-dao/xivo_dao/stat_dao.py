# -*- coding: utf-8 -*-

from xivo_dao.alchemy.dbconnection import get_connection

_STR_TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _get_session():
    return get_connection('asterisk').get_session()


def fill_simple_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_simple_calls(:start, :end)'
        )


def fill_answered_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_answered_calls(:start, :end)'
        )


def fill_leaveempty_calls(start, end):
    _run_sql_function_returning_void(
        start, end,
        'SELECT 1 AS place_holder FROM fill_leaveempty_calls(:start, :end)'
        )


def _run_sql_function_returning_void(start, end, function):
    start = start.strftime(_STR_TIME_FMT)
    end = end.strftime(_STR_TIME_FMT)

    (_get_session()
     .query('place_holder')
     .from_statement(function)
     .params(start=start, end=end)
     .first())


def get_login_intervals_in_range(start, end):
    logout_in_range = '''\
  SELECT
    stat_agent.id AS agent,
    CAST(time AS TIMESTAMP) AS logout,
    (
      SELECT
        CAST(time AS TIMESTAMP)
      FROM queue_log
      WHERE
        event IN ('AGENTCALLBACKLOGIN', 'AGENTLOGIN') AND
        agent = out.agent AND
        data1 = out.data1 AND
        time < out.time
      ORDER BY time DESC
      LIMIT 1
    ) AS login
  FROM queue_log AS out,
       stat_agent
  WHERE
    agent = stat_agent.name AND
    (time::timestamp BETWEEN :start AND :end) AND
    data1 <> '' AND
    event IN ('AGENTCALLBACKLOGOFF', 'AGENTLOGOFF')
  ORDER BY time ASC
'''

    rows = (_get_session()
            .query('agent', 'login', 'logout')
            .from_statement(logout_in_range)
            .params(start=start, end=end))

    results = {}

    for row in rows.all():
        if row.agent not in results:
            results[row.agent] = []

        start_time = row.login if row.login and row.login > start else start
        end_time = row.logout if row.logout and row.logout < end else end

        results[row.agent].append((start_time, end_time))

    login_in_range = '''\
SELECT
  stat_agent.id AS agent,
  CAST(time AS TIMESTAMP) AS login,
  (
    SELECT
      CAST(time AS TIMESTAMP)
    FROM queue_log
    WHERE
      event IN ('AGENTCALLBACKLOGOFF', 'AGENTLOGOFF') AND
      agent = out.agent AND
      data1 = out.data1 AND
      time > out.time
    ORDER BY time ASC
    LIMIT 1
  ) AS logout
FROM
  queue_log AS out,
  stat_agent
WHERE
  stat_agent.name = out.agent AND
  (time::TIMESTAMP BETWEEN :start AND :end) AND
  event IN ('AGENTCALLBACKLOGIN', 'AGENTLOGIN')
  ORDER BY time ASC
'''

    rows = (_get_session()
            .query('agent', 'login', 'logout')
            .from_statement(login_in_range)
            .params(start=start, end=end))

    for row in rows.all():
        if row.agent not in results:
            results[row.agent] = []

        start_time = row.login if row.login and row.login > start else start
        end_time = row.logout if row.logout and row.logout < end else end

        results[row.agent].append((start_time, end_time))

    unique_result = {}

    logged_before_start = '''\
SELECT stat_agent.id AS agent
FROM (
  SELECT agent FROM (
    SELECT DISTINCT ON (1) agent,
           time,
           event
     FROM queue_log
     WHERE
       (event IN ('AGENTLOGIN', 'AGENTCALLBACKLOGIN',
                  'AGENTLOGOFF', 'AGENTCALLBACKLOGOFF',
                  'CONNECT') AND
        time::TIMESTAMP <= :start) OR
       (event = 'CONNECT' AND
        (time::TIMESTAMP BETWEEN :start AND :end))
     ORDER BY agent, time DESC) as last_login_logoff
  WHERE last_login_logoff.event IN ('AGENTLOGIN',
                                    'AGENTCALLBACKLOGIN',
                                    'CONNECT')

  EXCEPT

  SELECT distinct(agent)
  FROM queue_log
  WHERE
    event IN ('AGENTLOGOFF',
              'AGENTCALLBACKLOGOFF',
              'AGENTLOGIN',
              'AGENTCALLBACKLOGIN') AND
    data1 <> '' AND
    (time::TIMESTAMP BETWEEN :start AND :end)) as difference, stat_agent
WHERE stat_agent.name = difference.agent
'''

    rows = (_get_session()
            .query('agent')
            .from_statement(logged_before_start)
            .params(start=start, end=end))

    for row in rows.all():
        results[row.agent] = [(start, end)]

    for agent, logins in results.iteritems():
        unique_result[agent] = sorted(list(set(logins)))

    return unique_result
