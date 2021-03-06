# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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

from __future__ import unicode_literals

import uuid
import re

from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint, Index, \
    UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.types import Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

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
        ForeignKeyConstraint(('voicemailid',),
                             ('voicemail.uniqueid',)),
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
    email = Column(String(128))
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
    func_key_template_id = Column(Integer, ForeignKey('func_key_template.id', ondelete="SET NULL"))
    func_key_private_template_id = Column(Integer, ForeignKey('func_key_template.id'), nullable=False)

    webi_lastname = Column('lastname', String(128), nullable=False, server_default='')
    webi_userfield = Column('userfield', String(128), nullable=False, server_default='')
    webi_description = Column('description', Text, nullable=False, default='')

    func_key_template = relationship(FuncKeyTemplate, foreign_keys=func_key_template_id)
    func_key_template_private = relationship(FuncKeyTemplate, foreign_keys=func_key_private_template_id)
    cti_profile = relationship(CtiProfile, foreign_keys=cti_profile_id)
    entity = relationship(Entity, foreign_keys=entityid)

    main_line_rel = relationship("UserLine",
                                 primaryjoin="""and_(UserFeatures.id == UserLine.user_id,
                                                     UserLine.main_line == True)""")
    voicemail = relationship("Voicemail")
    cti_profile = relationship("CtiProfile")

    def extrapolate_caller_id(self, extension=None):
        default_num = extension.exten if extension else None
        user_match = caller_id_regex.match(self.callerid)
        name = user_match.group('name')
        num = user_match.group('num')
        return name, (num or default_num)

    def has_private_template(self):
        return self.func_key_private_template_id is not None or self.func_key_template_private is not None

    def has_entity(self):
        return self.entity is not None or self.entityid is not None

    def fill_caller_id(self):
        if self.caller_id is None:
            self.caller_id = '"{}"'.format(self.fullname)

    @hybrid_property
    def fullname(self):
        name = self.firstname
        if self.lastname:
            name += " {}".format(self.lastname)
        return name

    @fullname.expression
    def fullname(cls):
        return func.trim(cls.firstname + " " + cls.webi_lastname)

    @hybrid_property
    def username(self):
        if self.loginclient == '':
            return None
        return self.loginclient

    @username.expression
    def username(cls):
        return func.nullif(cls.loginclient, '')

    @username.setter
    def username(self, value):
        if value is None:
            self.loginclient = ''
        else:
            self.loginclient = value

    @hybrid_property
    def password(self):
        if self.passwdclient == '':
            return None
        return self.passwdclient

    @password.expression
    def password(cls):
        return func.nullif(cls.passwdclient, '')

    @password.setter
    def password(self, value):
        if value is None:
            self.passwdclient = ''
        else:
            self.passwdclient = value

    @hybrid_property
    def entity_id(self):
        return self.entityid

    @entity_id.setter
    def entity_id(self, value):
        self.entityid = value

    @hybrid_property
    def caller_id(self):
        if self.callerid == '':
            return None
        return self.callerid

    @caller_id.expression
    def caller_id(cls):
        return func.nullif(cls.callerid, '')

    @caller_id.setter
    def caller_id(self, value):
        if value is None:
            self.callerid = ''
        else:
            self.callerid = value

    @hybrid_property
    def outgoing_caller_id(self):
        if self.outcallerid == '':
            return None
        return self.outcallerid

    @outgoing_caller_id.expression
    def outgoing_caller_id(cls):
        return func.nullif(cls.outcallerid, '')

    @outgoing_caller_id.setter
    def outgoing_caller_id(self, value):
        if value is None:
            self.outcallerid = ''
        else:
            self.outcallerid = value

    @hybrid_property
    def music_on_hold(self):
        if self.musiconhold == '':
            return None
        return self.musiconhold

    @music_on_hold.expression
    def music_on_hold(cls):
        return func.nullif(cls.musiconhold, '')

    @music_on_hold.setter
    def music_on_hold(self, value):
        if value is None:
            self.musiconhold = ''
        else:
            self.musiconhold = value

    @hybrid_property
    def mobile_phone_number(self):
        if self.mobilephonenumber == '':
            return None
        return self.mobilephonenumber

    @mobile_phone_number.expression
    def mobile_phone_number(cls):
        return func.nullif(cls.mobilephonenumber, '')

    @mobile_phone_number.setter
    def mobile_phone_number(self, value):
        if value is None:
            self.mobilephonenumber = ''
        else:
            self.mobilephonenumber = value

    @hybrid_property
    def voicemail_id(self):
        return self.voicemailid

    @voicemail_id.setter
    def voicemail_id(self, value):
        self.voicemailid = value

    @hybrid_property
    def userfield(self):
        if self.webi_userfield == '':
            return None
        return self.webi_userfield

    @userfield.expression
    def userfield(cls):
        return func.nullif(cls.webi_userfield, '')

    @userfield.setter
    def userfield(self, value):
        if value is None:
            self.webi_userfield = ''
        else:
            self.webi_userfield = value

    @hybrid_property
    def lastname(self):
        if self.webi_lastname == '':
            return None
        return self.webi_lastname

    @lastname.expression
    def lastname(cls):
        return func.nullif(cls.webi_lastname, '')

    @lastname.setter
    def lastname(self, value):
        if value is None:
            self.webi_lastname = ''
        else:
            self.webi_lastname = value

    @hybrid_property
    def description(self):
        if self.webi_description == '':
            return None
        return self.webi_description

    @description.expression
    def description(cls):
        return func.nullif(cls.webi_description, '')

    @description.setter
    def description(self, value):
        if value is None:
            self.webi_description = ''
        else:
            self.webi_description = value

    @hybrid_property
    def template_id(self):
        return self.func_key_template_id

    @template_id.setter
    def template_id(self, value):
        self.func_key_template_id = value

    @hybrid_property
    def private_template_id(self):
        return self.func_key_private_template_id

    @private_template_id.setter
    def private_template_id(self, value):
        self.func_key_private_template_id = value

    @hybrid_property
    def supervision_enabled(self):
        return self.enablehint == 1

    @supervision_enabled.setter
    def supervision_enabled(self, value):
        self.enablehint = int(value == 1) if value is not None else None

    @hybrid_property
    def call_transfer_enabled(self):
        return self.enablexfer == 1

    @call_transfer_enabled.setter
    def call_transfer_enabled(self, value):
        self.enablexfer = int(value == 1) if value is not None else None

    @hybrid_property
    def ring_seconds(self):
        return self.ringseconds

    @ring_seconds.setter
    def ring_seconds(self, value):
        self.ringseconds = value

    @hybrid_property
    def simultaneous_calls(self):
        return self.simultcalls

    @simultaneous_calls.setter
    def simultaneous_calls(self, value):
        self.simultcalls = value

    @hybrid_property
    def cti_enabled(self):
        return self.enableclient == 1

    @cti_enabled.setter
    def cti_enabled(self, value):
        self.enableclient = int(value == 1) if value is not None else None
