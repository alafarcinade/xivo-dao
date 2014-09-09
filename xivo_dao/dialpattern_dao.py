# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.dialpattern import DialPattern


@daosession
def delete(session, dialpattern_id):
    with commit_or_abort(session):
        return session.query(DialPattern).filter(DialPattern.id == dialpattern_id).delete()
