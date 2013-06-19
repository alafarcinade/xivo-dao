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


class AbstractModels(object):

    def __init__(self, *args, **kwargs):
        for model_field in self._MAPPING.itervalues():
            model_field_value = kwargs.get(model_field)
            if model_field_value is not None:
                setattr(self, model_field, model_field_value)

    def __eq__(self, other):
        class_name = self.__class__.__name__
        if not isinstance(other, self.__class__):
            raise TypeError('Must compare a %s with another %s' % (class_name, class_name))

        return self.__dict__ == other.__dict__

    @classmethod
    def from_data_source(cls, db_object):
        for db_field, model_field in cls._MAPPING.iteritems():
            if hasattr(db_object, db_field):
                model_field_value = getattr(db_object, db_field)
                setattr(cls, model_field, model_field_value)
        return cls()

    def to_data_source(self, class_schema):
        db_object = class_schema()
        for db_field, model_field in self._MAPPING.iteritems():
            if hasattr(self, model_field):
                field_value = getattr(self, model_field)
                setattr(db_object, db_field, field_value)
        return db_object

    @classmethod
    def from_user_data(cls, properties):
        return cls(**properties)

    def missing_parameters(self):
        missing = []

        for parameter in self.MANDATORY:
            try:
                attribute = getattr(self, parameter)
                if attribute is None:
                    missing.append(parameter)
            except AttributeError:
                missing.append(parameter)

        return missing
