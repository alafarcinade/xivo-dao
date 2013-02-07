# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
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

from datetime import datetime
from xivo_dao.helpers.cel_exception import InvalidInputException
import logging
import sys
import traceback
#from xivo_restapi.dao.recording_details_dao import RecordingDetailsDao

logger = logging.getLogger(__name__)


def table_to_string(class_instance):
    members = vars(class_instance)
    result = ""
    for n in sorted(set(members)):
        if not n.startswith('_'):
            result += str(n) + ": " + \
                        str(getattr(class_instance, n)) + \
                        ','

    return result.rstrip(',')


def table_list_to_list_dict(list_instance):
    list_of_dict = []

    for class_instance in list_instance:
        for key in dir(class_instance.__class__):
            if not key.startswith('_'):
                getattr(class_instance, key)
                break
        dict_instance = {}
        members = vars(class_instance)
        logger.debug("members = " + str(members))
        for elem in sorted(set(members)):
            logger.debug("Entering for: " + str(elem))
            if not elem.startswith('_'):
                value = getattr(class_instance, elem)
                #pour éviter d'avoir None au lieu de '' dans le résultat
                if value == None:
                    value = ''
                if type(value).__name__ != 'unicode':
                    value = str(value)
                else:
                    value = value.encode('utf-8', 'ignore')
                dict_instance[str(elem)] = value
        list_of_dict.append(dict_instance)
    return list_of_dict


def str_to_datetime(string):
    if(type(string) != str and type(string) != unicode):
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
    if (len(string) != 10 and len(string) != 19):
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
    try:
        if(len(string) == 10):
            result = datetime.strptime(string, "%Y-%m-%d")
            return result
        elif(len(string) == 19):
            return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
