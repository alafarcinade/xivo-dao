# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_dao.resources.features.model import TransferExtension


class TransferExtensionConverter(object):

    TRANSFERS = {'blindxfer': 'blind',
                 'atxfer': 'attended'}

    def var_names(self):
        return self.TRANSFERS.keys()

    def to_model(self, row):
        transfer = self.TRANSFERS[row.var_name]
        exten = row.var_val
        return TransferExtension(id=row.id,
                                 exten=exten,
                                 transfer=transfer)


transfer_converter = TransferExtensionConverter()
