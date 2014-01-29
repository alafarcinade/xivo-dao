# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
from xivo_dao.data_handler.configuration import dao, validator, notifier


def get_live_reload_status():
    enabled = dao.is_live_reload_enabled()
    return {'enabled': enabled}


def set_live_reload_status(data):
    validator.validate_live_reload_data(data)
    dao.set_live_reload_status(data)
    notifier.live_reload_status_changed(data)
