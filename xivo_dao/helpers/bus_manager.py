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

import logging

logger = logging.getLogger(__name__)
_bus_client = None
_exchange_name = None


def install_bus_event_producer(bus_producer, exchange_name):
    global _bus_client
    global _exchange_name
    _bus_client = bus_producer
    _exchange_name = exchange_name


def send_bus_event(event, routing_key):
    if not _bus_client:
        logger.warning('Trying to send %s on %s with an unconfigured bus', event, routing_key)
        return

    _bus_client.publish_event(_exchange_name, routing_key, event)
