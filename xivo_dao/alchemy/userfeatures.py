# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import uuid
import re

from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint, Index, \
    UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.types import Integer, String, Text
from sqlalchemy.orm import relationship

from xivo_dao.alchemy import enum
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.entity import Entity
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.helpers.db_manager import Base


def _new_uuid():
    return str(uuid.uuid4())


caller_id_regex = re.compile(r'''
                             "                      #name start
                             (?P<name>[^"]+)        #inside ""
                             "                      #name end
                             \s*                    #space between name and number
                             (
                             <                      #number start
                             (?P<num>\+?[\dA-Z]+)   #inside <>
                             >                      #number end
                             )?                     #number is optional
                             ''', re.VERBOSE)


class UserFeatures(Base):

    __tablename__ = 'userfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('cti_profile_id',),
                             ('cti_profile.id',),
                             ondelete='RESTRICT'),
        ForeignKeyConstraint(('entityid',),
                             ('entity.id',),
                             ondelete='RESTRICT'),
        UniqueConstraint('func_key_private_template_id'),
        UniqueConstraint('uuid', name='userfeatures_uuid'),
        Index('userfeatures__idx__agentid', 'agentid'),
        Index('userfeatures__idx__entityid', 'entityid'),
        Index('userfeatures__idx__firstname', 'firstname'),
        Index('userfeatures__idx__lastname', 'lastname'),
        Index('userfeatures__idx__loginclient', 'loginclient'),
        Index('userfeatures__idx__musiconhold', 'musiconhold'),
        Index('userfeatures__idx__uuid', 'uuid'),
        Index('userfeatures__idx__voicemailid', 'voicemailid'),
    )

    id = Column(Integer, nullable=False)
    uuid = Column(String(38), nullable=False, default=_new_uuid)
    firstname = Column(String(128), nullable=False, server_default='')
    lastname = Column(String(128), nullable=False, server_default='')
    voicemailid = Column(Integer)
    agentid = Column(Integer)
    pictureid = Column(Integer)
    entityid = Column(Integer)
    callerid = Column(String(160))
    ringseconds = Column(Integer, nullable=False, server_default='30')
    simultcalls = Column(Integer, nullable=False, server_default='5')
    enableclient = Column(Integer, nullable=False, server_default='0')
    loginclient = Column(String(64), nullable=False, server_default='')
    passwdclient = Column(String(64), nullable=False, server_default='')
    cti_profile_id = Column(Integer)
    enablehint = Column(Integer, nullable=False, server_default='1')
    enablevoicemail = Column(Integer, nullable=False, server_default='0')
    enablexfer = Column(Integer, nullable=False, server_default='1')
    enableonlinerec = Column(Integer, nullable=False, server_default='0')
    callrecord = Column(Integer, nullable=False, server_default='0')
    incallfilter = Column(Integer, nullable=False, server_default='0')
    enablednd = Column(Integer, nullable=False, server_default='0')
    enableunc = Column(Integer, nullable=False, server_default='0')
    destunc = Column(String(128), nullable=False, server_default='')
    enablerna = Column(Integer, nullable=False, server_default='0')
    destrna = Column(String(128), nullable=False, server_default='')
    enablebusy = Column(Integer, nullable=False, server_default='0')
    destbusy = Column(String(128), nullable=False, server_default='')
    musiconhold = Column(String(128), nullable=False, server_default='')
    outcallerid = Column(String(80), nullable=False, server_default='')
    mobilephonenumber = Column(String(128), nullable=False, server_default='')
    userfield = Column(String(128), nullable=False, server_default='')
    bsfilter = Column(enum.generic_bsfilter, nullable=False, server_default='no')
    preprocess_subroutine = Column(String(39))
    timezone = Column(String(128))
    language = Column(String(20))
    ringintern = Column(String(64))
    ringextern = Column(String(64))
    ringgroup = Column(String(64))
    ringforward = Column(String(64))
    rightcallcode = Column(String(16))
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text, nullable=False, default='')
    func_key_template_id = Column(Integer, ForeignKey('func_key_template.id', ondelete="SET NULL"))
    func_key_private_template_id = Column(Integer, ForeignKey('func_key_template.id'), nullable=False)

    func_key_template = relationship(FuncKeyTemplate, foreign_keys=func_key_template_id)
    func_key_template_private = relationship(FuncKeyTemplate, foreign_keys=func_key_private_template_id)
    cti_profile = relationship(CtiProfile, foreign_keys=cti_profile_id)
    entity = relationship(Entity, foreign_keys=entityid)

    @property
    def fullname(self):
        return ' '.join([self.firstname, self.lastname])

    def extrapolate_caller_id(self, extension=None):
        default_num = extension.exten if extension else None
        user_match = caller_id_regex.match(self.callerid)
        name = user_match.group('name')
        num = user_match.group('num')
        return name, (num or default_num)
