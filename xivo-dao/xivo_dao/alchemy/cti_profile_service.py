# -*- coding: utf-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
from xivo_dao.alchemy.base import Base


class CtiProfileService(Base):

    __tablename__ = 'cti_profile_service'

    profile_id = Column(Integer, ForeignKey('cti_profile.id'), primary_key=True)
    service_id = Column(Integer, ForeignKey("cti_service.id"), primary_key=True)
