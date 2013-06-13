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

from xivo_dao.helpers.db_manager import BusPublisher
from xivo_dao.notifiers.command.user.common import UpdateUserCommand, \
    CreateUserCommand, DeleteUserCommand


def user_created(user_id):
    BusPublisher.execute_command(CreateUserCommand(user_id))


def user_updated(user_id):
    BusPublisher.execute_command(UpdateUserCommand(user_id))


def user_deleted(user_id):
    BusPublisher.execute_command(DeleteUserCommand(user_id))
