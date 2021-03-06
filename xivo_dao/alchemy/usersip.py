# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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

from collections import Iterable

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers import errors
from sqlalchemy.schema import Column
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.schema import Index
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Integer, String, Text, Enum
from xivo_dao.alchemy import enum

EXCLUDE_OPTIONS = {'id',
                   'commented',
                   'options'}
EXCLUDE_OPTIONS_CONFD = {'name',
                         'username',
                         'secret',
                         'type',
                         'host',
                         'context',
                         'category'}


class UserSIP(Base):

    __tablename__ = 'usersip'

    id = Column(Integer, nullable=False)
    name = Column(String(40), nullable=False)
    type = Column(Enum('friend', 'peer', 'user',
                       name='useriax_type',
                       metadata=Base.metadata),
                  nullable=False)
    username = Column(String(80))
    secret = Column(String(80), nullable=False, server_default='')
    md5secret = Column(String(32), nullable=False, server_default='')
    context = Column(String(39))
    language = Column(String(20))
    accountcode = Column(String(20))
    amaflags = Column(Enum('default', 'omit', 'billing', 'documentation',
                           name='useriax_amaflags',
                           metadata=Base.metadata),
                      nullable=False, server_default='default')
    allowtransfer = Column(Integer)
    fromuser = Column(String(80))
    fromdomain = Column(String(255))
    subscribemwi = Column(Integer, nullable=False, server_default='0')
    buggymwi = Column(Integer)
    call_limit = Column('call-limit', Integer, nullable=False, server_default='10')
    callerid = Column(String(160))
    fullname = Column(String(80))
    cid_number = Column(String(80))
    maxcallbitrate = Column(Integer)
    insecure = Column(Enum('port', 'invite', 'port,invite',
                           name='usersip_insecure',
                           metadata=Base.metadata))
    nat = Column(Enum('no', 'force_rport', 'comedia', 'force_rport,comedia',
                      name='usersip_nat',
                      metadata=Base.metadata))
    promiscredir = Column(Integer)
    usereqphone = Column(Integer)
    videosupport = Column(Enum('no', 'yes', 'always',
                               name='usersip_videosupport',
                               metadata=Base.metadata))
    trustrpid = Column(Integer)
    sendrpid = Column(String(16))
    allowsubscribe = Column(Integer)
    allowoverlap = Column(Integer)
    dtmfmode = Column(Enum('rfc2833', 'inband', 'info', 'auto',
                           name='usersip_dtmfmode',
                           metadata=Base.metadata))
    rfc2833compensate = Column(Integer)
    qualify = Column(String(4))
    g726nonstandard = Column(Integer)
    disallow = Column(String(100))
    allow = Column(Text)
    autoframing = Column(Integer)
    mohinterpret = Column(String(80))
    useclientcode = Column(Integer)
    progressinband = Column(Enum('no', 'yes', 'never',
                                 name='usersip_progressinband',
                                 metadata=Base.metadata))
    t38pt_udptl = Column(Integer)
    t38pt_usertpsource = Column(Integer)
    rtptimeout = Column(Integer)
    rtpholdtimeout = Column(Integer)
    rtpkeepalive = Column(Integer)
    deny = Column(String(31))
    permit = Column(String(31))
    defaultip = Column(String(255))
    setvar = Column(String(100), nullable=False, server_default='')
    host = Column(String(255), nullable=False, server_default='dynamic')
    port = Column(Integer)
    regexten = Column(String(80))
    subscribecontext = Column(String(80))
    fullcontact = Column(String(255))
    vmexten = Column(String(40))
    callingpres = Column(Integer)
    ipaddr = Column(String(255), nullable=False, server_default='')
    regseconds = Column(Integer, nullable=False, server_default='0')
    regserver = Column(String(20))
    lastms = Column(String(15), nullable=False, server_default='')
    parkinglot = Column(Integer)
    protocol = Column(enum.trunk_protocol, nullable=False, server_default='sip')
    category = Column(Enum('user', 'trunk',
                           name='useriax_category',
                           metadata=Base.metadata),
                      nullable=False)
    outboundproxy = Column(String(1024))
    transport = Column(String(255))
    remotesecret = Column(String(255))
    directmedia = Column(String(20))
    callcounter = Column(Integer)
    busylevel = Column(Integer)
    ignoresdpversion = Column(Integer)
    session_timers = Column('session-timers',
                            Enum('originate', 'accept', 'refuse',
                                 name='usersip_session_timers',
                                 metadata=Base.metadata))
    session_expires = Column('session-expires', Integer)
    session_minse = Column('session-minse', Integer)
    session_refresher = Column('session-refresher',
                               Enum('uac', 'uas',
                                    name='usersip_session_refresher',
                                    metadata=Base.metadata))
    callbackextension = Column(String(255))
    registertrying = Column(Integer)
    timert1 = Column(Integer)
    timerb = Column(Integer)
    qualifyfreq = Column(Integer)
    contactpermit = Column(String(1024))
    contactdeny = Column(String(1024))
    unsolicited_mailbox = Column(String(1024))
    use_q850_reason = Column(Integer)
    encryption = Column(Integer)
    snom_aoc_enabled = Column(Integer)
    maxforwards = Column(Integer)
    disallowed_methods = Column(String(1024))
    textsupport = Column(Integer)
    commented = Column(Integer, nullable=False, server_default='0')
    _options = Column("options", ARRAY(String, dimensions=2),
                      nullable=False, default=list, server_default='{}')

    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('usersip__idx__category', 'category'),
        CheckConstraint(
            directmedia.in_(
                ['no', 'yes', 'nonat', 'update', 'update,nonat', 'outgoing'])),
    )

    @property
    def options(self):
        return self.all_options(EXCLUDE_OPTIONS_CONFD)

    def all_options(self, exclude=None):
        native_options = list(self.native_options(exclude))
        return native_options + self._options

    def native_options(self, exclude=None):
        for column in self.native_option_names(exclude):
            for value in self.native_option(column):
                yield [column, value]

    def native_option(self, column_name):
        if column_name == 'subscribemwi':
            yield 'yes' if self.subscribemwi == 1 else 'no'
        elif column_name == 'regseconds':
            yield unicode(self.regseconds)
        elif column_name == 'allow':
            if self.allow:
                for value in self.allow.split(","):
                    yield value
        else:
            value = getattr(self, self._attribute(column_name), None)
            if value is not None and value != "":
                yield unicode(value)

    @options.setter
    def options(self, options):
        option_names = self.native_option_names(EXCLUDE_OPTIONS_CONFD)
        self.reset_options()
        self.set_options(option_names, options)

    def reset_options(self):
        self.reset_extra_options()
        self.reset_native_options()

    def reset_extra_options(self):
        self._options = []

    def reset_native_options(self):
        defaults = self.option_defaults()
        for column in self.native_option_names(EXCLUDE_OPTIONS_CONFD):
            value = defaults.get(column, None)
            setattr(self, self._attribute(column), value)

    def set_options(self, option_names, options):
        self.validate_options(options)
        for option in options:
            self.validate_option(option)
            column, value = option
            if column in option_names:
                self.set_native_option(column, value)
            else:
                self.add_extra_option(column, value)

    def validate_options(self, options):
        if not isinstance(options, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')

    def validate_option(self, option):
        if not isinstance(option, Iterable):
            raise errors.wrong_type('options', 'list of pair of strings')
        if not len(option) == 2:
            raise errors.wrong_type('options', 'list of pair of strings')
        for i in option:
            if not isinstance(i, (str, unicode)):
                raise errors.wrong_type('options', "value '{}' is not a string".format(i))

    def set_native_option(self, column, value):
        if column == 'subscribemwi':
            self.subscribemwi = 1 if value == 'yes' else 0
        elif column == 'allow':
            allow = self.allow.split(',') if self.allow else []
            allow.append(value)
            self.allow = ",".join(allow)
        else:
            setattr(self, self._attribute(column), value)

    def add_extra_option(self, name, value):
        self._options.append([name, value])

    def native_option_names(self, exclude=None):
        exclude = set(exclude or []).union(EXCLUDE_OPTIONS)
        return set(column.name for column in self.__table__.columns) - exclude

    def option_defaults(self):
        defaults = {}
        for column in self.__table__.columns:
            if column.server_default:
                defaults[column.name] = column.server_default.arg
        return defaults

    def same_protocol(self, protocol, id):
        return protocol == 'sip' and self.id == id

    def update_caller_id(self, user, extension=None):
        name, num = user.extrapolate_caller_id(extension)
        self.callerid = u'"{}"'.format(name)
        if num:
            self.callerid += " <{}>".format(num)

    def update_setvar(self, user):
        self.setvar = 'XIVO_USERID={}'.format(user.id)

    def clear_caller_id(self):
        self.callerid = None

    def clear_setvar(self):
        self.setvar = ''

    def endpoint_protocol(self):
        return 'sip'

    def _attribute(self, column_name):
        return column_name.replace("-", "_")
