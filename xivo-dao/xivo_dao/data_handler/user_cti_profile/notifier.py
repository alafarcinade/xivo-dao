# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_bus.resources.user_cti_profile import event
from xivo_dao.helpers import bus_manager


def associated(user_cti_profile):
    bus_event = event.UserCtiProfileAssociatedEvent(user_cti_profile.user_id,
                                                    user_cti_profile.cti_profile_id)
    bus_manager.send_bus_command(bus_event)

def dissociated(user_cti_profile):
    bus_event = event.UserCtiProfileDissociatedEvent(user_cti_profile.user_id,
                                                    user_cti_profile.cti_profile_id)
    bus_manager.send_bus_command(bus_event)
