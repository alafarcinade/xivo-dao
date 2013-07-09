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

from urllib2 import URLError
from xivo_dao.data_handler.user import dao as user_dao, notifier
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementAlreadyExistsError
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.voicemail import services as voicemail_services
from xivo_dao.helpers import provd_connector


def get(user_id):
    return user_dao.get(user_id)


def get_by_number_context(number, context):
    return user_dao.get_by_number_context(number, context)


def find_all(order=None):
    return user_dao.find_all(order=order)


def find_by_firstname_lastname(firstname, lastname):
    return user_dao.find_user(firstname, lastname)


def create(user):
    _validate(user)
    _check_for_existing_user(user)
    user = user_dao.create(user)
    notifier.created(user)
    return user


def edit(user):
    _validate(user)
    user_dao.edit(user)
    _update_voicemail_fullname(user)
    notifier.edited(user)


def delete(user):
    user_dao.delete(user)
    notifier.deleted(user)


def delete_voicemail(user):
    try:
        voicemail = voicemail_services.get(user.voicemail_id)
    except LookupError:
        return
    else:
        voicemail_services.delete(voicemail)


def delete_line(user):
    try:
        line = line_services.get_by_user_id(user.id)
    except LookupError:
        return
    else:
        if line.deviceid is not None:
            try:
                _provd_remove_line(line.deviceid, line.num)
            except URLError as e:
                raise provd_connector.ProvdError(str(e))
            line_services.delete(line)


def _validate(user):
    _check_missing_parameters(user)
    _check_invalid_parameters(user)


def _check_missing_parameters(user):
    missing = user.missing_parameters()
    if missing:
        raise MissingParametersError(missing)


def _check_invalid_parameters(user):
    invalid_parameters = []
    if not user.firstname:
        invalid_parameters.append('firstname')
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)


def _check_for_existing_user(user):
    if user_dao.find_user(user.firstname, user.lastname):
        raise ElementAlreadyExistsError('User', user.firstname, user.lastname)


def _update_voicemail_fullname(user):
    if hasattr(user, 'voicemail_id') and user.voicemail_id is not None:
        voicemail = voicemail_services.get(user.voicemail_id)
        voicemail.fullname = user.fullname
        voicemail_services.edit(voicemail)


def _provd_remove_line(deviceid, linenum):
    config = provd_connector.config_manager.get(deviceid)
    del config["raw_config"]["sip_lines"][str(linenum)]
    if len(config["raw_config"]["sip_lines"]) == 0:
        # then we reset to autoprov
        _reset_config(config)
        _reset_device_to_autoprov(deviceid)
    provd_connector.config_manager.update(config)


def _reset_config(config):
    del config["raw_config"]["sip_lines"]
    if "funckeys" in config["raw_config"]:
        del config["raw_config"]["funckeys"]


def _reset_device_to_autoprov(deviceid):
    device = provd_connector.device_manager.get(deviceid)
    new_configid = provd_connector.config_manager.autocreate()
    device["config"] = new_configid
    provd_connector.device_manager.update(device)
