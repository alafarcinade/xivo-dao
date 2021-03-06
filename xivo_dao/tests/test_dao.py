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

from __future__ import unicode_literals

import datetime
import itertools
import logging
import os
import random
import unittest
import time
import string

from xivo_dao.alchemy.accessfeatures import AccessFeatures
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.cti_contexts import CtiContexts
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.directories import Directories
from xivo_dao.alchemy.entity import Entity as EntitySchema
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate
from xivo_dao.alchemy.func_key_type import FuncKeyType
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.infos import Infos
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.alchemy.musiconhold import MusicOnHold
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.queueinfo import QueueInfo
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queueskill import QueueSkill
from xivo_dao.alchemy.queueskillrule import QueueSkillRule
from xivo_dao.alchemy.sccpdevice import SCCPDevice as SCCPDeviceSchema
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPLineSchema
from xivo_dao.alchemy.sipauthentication import SIPAuthentication
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticmeetme import StaticMeetme
from xivo_dao.alchemy.staticqueue import StaticQueue
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.alchemy.user import User
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom as UserCustomSchema
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.helpers import db_manager
from xivo_dao.helpers.db_manager import Base
from xivo.debug import trace_duration

from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

logger = logging.getLogger(__name__)

_create_tables = True

TEST_DB_URL = os.getenv('XIVO_TEST_DB_URL', 'postgresql://asterisk:asterisk@localhost/asterisktest')


def expensive_setup():
    global _create_tables
    if _create_tables and (os.environ.get('CREATE_TABLES', '1') == '1'):
        _init_tables()
        _create_tables = False


@trace_duration
def _init_tables():
    logger.debug("Cleaning tables")
    Base.metadata.reflect()
    logger.debug("drop all tables")
    Base.metadata.drop_all()
    logger.debug("create all tables")
    Base.metadata.create_all()
    logger.debug("Tables cleaned")


Session = sessionmaker()

engine = None


class DAOTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global engine
        if not engine:
            engine = create_engine(TEST_DB_URL, poolclass=StaticPool)

        cls.engine = Base.metadata.bind = engine
        expensive_setup()

    def setUp(self):
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()

        db_manager.Session.configure(bind=self.connection)
        self.session = db_manager.Session

        self.session.begin_nested()

        @event.listens_for(self.session, 'after_transaction_end')
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.expire_all()
                session.begin_nested()

    def tearDown(self):
        self.session.close()
        self.session.remove()
        self.trans.rollback()

    def add_admin(self, **kwargs):
        admin = User(**kwargs)
        self.add_me(admin)
        return admin

    def add_user_line_with_exten(self, **kwargs):
        kwargs.setdefault('firstname', 'unittest')
        kwargs.setdefault('lastname', 'unittest')
        kwargs.setdefault('callerid', u'"%s %s"' % (kwargs['firstname'], kwargs['lastname']))
        kwargs.setdefault('exten', '%s' % random.randint(1000, 1999))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('protocol', 'sip')
        kwargs.setdefault('protocolid', self._generate_int())
        kwargs.setdefault('name_line', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('commented_line', 0)
        kwargs.setdefault('device', 1)
        kwargs.setdefault('voicemail_id', None)
        kwargs.setdefault('musiconhold', 'default')
        kwargs.setdefault('agentid', None)
        kwargs.setdefault('mobilephonenumber', '')
        kwargs.setdefault('description', '')
        kwargs.setdefault('userfield', '')

        user = self.add_user(firstname=kwargs['firstname'],
                             lastname=kwargs['lastname'],
                             callerid=kwargs['callerid'],
                             voicemailid=kwargs['voicemail_id'],
                             musiconhold=kwargs['musiconhold'],
                             agentid=kwargs['agentid'],
                             mobilephonenumber=kwargs['mobilephonenumber'],
                             userfield=kwargs['userfield'],
                             description=kwargs['description'])
        line = self.add_line(context=kwargs['context'],
                             protocol=kwargs['protocol'],
                             protocolid=kwargs['protocolid'],
                             name=kwargs['name_line'],
                             device=kwargs['device'],
                             commented=kwargs['commented_line'])
        extension = self.add_extension(exten=kwargs['exten'],
                                       context=kwargs['context'],
                                       typeval=user.id)
        user_line = self.add_user_line(line_id=line.id,
                                       user_id=user.id,
                                       extension_id=extension.id)

        user_line.user = user
        user_line.line = line
        user_line.extension = extension

        return user_line

    def add_user_line_without_exten(self, **kwargs):
        kwargs.setdefault('firstname', 'unittest')
        kwargs.setdefault('lastname', 'unittest')
        kwargs.setdefault('callerid', u'"%s %s"' % (kwargs['firstname'], kwargs['lastname']))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('protocol', 'sip')
        kwargs.setdefault('protocolid', self._generate_int())
        kwargs.setdefault('name_line', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('commented_line', 0)
        kwargs.setdefault('device', 1)
        kwargs.setdefault('voicemail_id', None)
        kwargs.setdefault('agentid', None)
        kwargs.setdefault('mobilephonenumber', '+14184765458')

        user = self.add_user(firstname=kwargs['firstname'],
                             lastname=kwargs['lastname'],
                             callerid=kwargs['callerid'],
                             voicemailid=kwargs['voicemail_id'],
                             mobilephonenumber=kwargs['mobilephonenumber'],
                             agentid=kwargs['agentid'])
        line = self.add_line(context=kwargs['context'],
                             protocol=kwargs['protocol'],
                             protocolid=kwargs['protocolid'],
                             name=kwargs['name_line'],
                             device=kwargs['device'],
                             commented=kwargs['commented_line'])
        user_line = self.add_user_line(line_id=line.id,
                                       user_id=user.id)

        user_line.user = user
        user_line.line = line

        return user_line

    def add_user_line_without_user(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('protocol', 'sip')
        kwargs.setdefault('protocolid', self._generate_int())
        kwargs.setdefault('provisioningid', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('device', 1)

        kwargs.setdefault('exten', None)
        kwargs.setdefault('type', 'user')

        line = self.add_line(name=kwargs['name'],
                             context=kwargs['context'],
                             protocol=kwargs['protocol'],
                             protocolid=kwargs['protocolid'],
                             provisioningid=kwargs['provisioningid'],
                             device=kwargs['device'])
        extension = self.add_extension(exten=kwargs['exten'],
                                       context=kwargs['context'],
                                       type=kwargs['type'])
        user_line = self.add_user_line(line_id=line.id, extension_id=extension.id)

        user_line.extension = extension
        user_line.line = line

        return user_line

    def add_line(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('protocol', kwargs.get('endpoint', 'sip'))
        kwargs.setdefault('protocolid', kwargs.get('endpoint_id', self._generate_int()))
        kwargs.setdefault('provisioningid', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('id', self._generate_int())

        line = LineFeatures(**kwargs)
        self.add_me(line)
        return line

    def add_context(self, **kwargs):
        kwargs.setdefault('entity', 'entity_id')
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('displayname', kwargs['name'].capitalize())
        kwargs.setdefault('description', 'Auto create context')

        context = Context(**kwargs)
        self.add_me(context)
        return context

    def add_context_include(self, **kwargs):
        kwargs.setdefault('context', self._random_name())
        kwargs.setdefault('include', self._random_name())
        kwargs.setdefault('priority', 0)

        context_include = ContextInclude(**kwargs)
        self.add_me(context_include)
        return context_include

    def add_context_number(self, **kwargs):
        kwargs.setdefault('type', 'user')
        context_number = ContextNumbers(**kwargs)
        self.add_me(context_number)
        return context_number

    def add_cti_context(self, **kwargs):
        kwargs.setdefault('name', '')
        kwargs.setdefault('directories', '')
        kwargs.setdefault('display', '')

        cti_context = CtiContexts(**kwargs)
        self.add_me(cti_context)
        return cti_context

    def add_user_line(self, **kwargs):
        kwargs.setdefault('main_user', True)
        kwargs.setdefault('main_line', True)
        kwargs.setdefault('id', self._generate_int())

        user_line = UserLine(**kwargs)
        self.add_me(user_line)
        return user_line

    def add_extension(self, **kwargs):
        kwargs.setdefault('type', 'user')
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('id', self._generate_int())

        extension = Extension(**kwargs)
        self.add_me(extension)
        return extension

    def add_incall(self, **kwargs):
        kwargs.setdefault('description', '')
        kwargs.setdefault('exten', '1000')
        kwargs.setdefault('context', 'from-extern')
        kwargs.setdefault('commented', 0)

        incall = Incall(**kwargs)
        self.add_me(incall)
        return incall

    def add_user(self, **kwargs):
        if 'func_key_private_template_id' not in kwargs:
            func_key_template = self.add_func_key_template(private=True)
            kwargs['func_key_private_template_id'] = func_key_template.id

        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('firstname', 'John')

        fullname = kwargs['firstname']
        if 'lastname' in kwargs:
            fullname += " " + kwargs['lastname']

        kwargs.setdefault('callerid', '"{}"'.format(fullname))
        user = UserFeatures(**kwargs)
        self.add_me(user)
        return user

    def add_agent(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('numgroup', self._generate_int())
        kwargs.setdefault('number', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('passwd', '')
        kwargs.setdefault('context', self._random_name())
        kwargs.setdefault('language', random.choice(['fr_FR', 'en_US']))
        kwargs.setdefault('description', 'description')
        agent = AgentFeatures(**kwargs)
        self.add_me(agent)
        return agent

    def add_group(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('context', '')
        group = GroupFeatures(**kwargs)
        self.add_me(group)
        return group

    def add_queuefeatures(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('displayname', kwargs['name'].capitalize())
        queuefeatures = QueueFeatures(**kwargs)
        self.add_me(queuefeatures)
        return queuefeatures

    def add_queue_info(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('call_time_t', int(time.time()))
        kwargs.setdefault('queue_name', self._random_name())
        kwargs.setdefault('hold_time', self._generate_int())
        kwargs.setdefault('talk_time', self._generate_int())
        kwargs.setdefault('caller_uniqueid', str(self._generate_int()))
        qi = QueueInfo(**kwargs)
        self.add_me(qi)
        return qi

    def add_meetmefeatures(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('meetmeid', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('confno', ''.join(random.choice('0123456789') for _ in range(6)))
        kwargs.setdefault('context', self._random_name())
        kwargs.setdefault('admin_identification', 'all')
        kwargs.setdefault('admin_mode', 'all')
        kwargs.setdefault('admin_announcejoinleave', 'no')
        kwargs.setdefault('user_mode', 'all')
        kwargs.setdefault('user_announcejoinleave', 'no')
        kwargs.setdefault('emailbody', '')
        kwargs.setdefault('description', '')
        meetmefeatures = MeetmeFeatures(**kwargs)
        self.add_me(meetmefeatures)
        return meetmefeatures

    def add_queue(self, **kwargs):
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('category', random.choice(['group', 'queue']))
        queue = Queue(**kwargs)
        self.add_me(queue)
        return queue

    def add_queue_skill(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('catid', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('description', '')
        queue_skill = QueueSkill(**kwargs)
        self.add_me(queue_skill)
        return queue_skill

    def add_queue_skill_rule(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', self._random_name())
        kwargs.setdefault('rule', self._random_name())
        queue_skill_rule = QueueSkillRule(**kwargs)
        self.add_me(queue_skill_rule)
        return queue_skill_rule

    def add_queue_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'queues.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_queue = StaticQueue(**kwargs)
        self.add_me(static_queue)
        return static_queue

    def add_queue_member(self, **kwargs):
        kwargs.setdefault('queue_name', self._random_name())
        kwargs.setdefault('interface', self._random_name())
        kwargs.setdefault('usertype', random.choice(['user', 'agent']))
        kwargs.setdefault('category', random.choice(['group', 'queue']))
        kwargs.setdefault('channel', self._random_name())
        kwargs.setdefault('userid', self._generate_int())

        queue_member = QueueMember(**kwargs)
        self.add_me(queue_member)
        return queue_member

    def add_pickup(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))

        pickup = Pickup(**kwargs)
        self.add_me(pickup)
        return pickup

    def add_pickup_member(self, **kwargs):
        kwargs.setdefault('pickupid', self._generate_int())
        kwargs.setdefault('category', random.choice(['pickup', 'member']))
        kwargs.setdefault('membertype', random.choice(['group', 'queue', 'user']))
        kwargs.setdefault('memberid', self._generate_int())

        pickup_member = PickupMember(**kwargs)
        self.add_me(pickup_member)
        return pickup_member

    def add_dialpattern(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('type', 'outcall')
        kwargs.setdefault('typeid', self._generate_int())
        kwargs.setdefault('exten', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        dialpattern = DialPattern(**kwargs)
        self.add_me(dialpattern)
        return dialpattern

    def add_dialaction(self, **kwargs):
        dialaction = Dialaction(**kwargs)
        self.add_me(dialaction)
        return dialaction

    def add_directory(self, **kwargs):
        directory_args = {'name': kwargs['name'],
                          'dirtype': kwargs['dirtype']}
        if 'uri' in kwargs:
            directory_args['uri'] = kwargs['uri']
        else:
            directory_args['uri'] = self._random_name()

        directory = Directories(**directory_args)
        self.add_me(directory)

        cti_directory = CtiDirectories(name=directory_args['name'],
                                       uri=directory_args['uri'],
                                       match_direct='')
        self.add_me(cti_directory)

    def add_usersip(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('type', 'friend')
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('category', 'user')

        usersip = UserSIP(**kwargs)
        self.add_me(usersip)
        return usersip

    def add_useriax(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('type', 'friend')
        kwargs.setdefault('category', 'user')

        useriax = UserIAX(**kwargs)
        self.add_me(useriax)
        return useriax

    def add_usercustom(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('interface', self._random_name())
        kwargs.setdefault('category', 'user')

        usercustom = UserCustomSchema(**kwargs)
        self.add_me(usercustom)
        return usercustom

    def add_sccpdevice(self, **kwargs):
        kwargs.setdefault('name', 'SEP001122334455')
        kwargs.setdefault('device', 'SEP001122334455')
        kwargs.setdefault('line', '1000')
        kwargs.setdefault('id', self._generate_int())

        sccpdevice = SCCPDeviceSchema(**kwargs)
        self.add_me(sccpdevice)
        return sccpdevice

    def add_sccpline(self, **kwargs):
        kwargs.setdefault('name', '1234')
        kwargs.setdefault('context', 'default')
        kwargs.setdefault('cid_name', 'Tester One')
        kwargs.setdefault('cid_num', '1234')
        kwargs.setdefault('id', self._generate_int())

        sccpline = SCCPLineSchema(**kwargs)
        self.add_me(sccpline)
        return sccpline

    def add_function_key_to_user(self, **kwargs):
        kwargs.setdefault('iduserfeatures', self._generate_int())
        kwargs.setdefault('fknum', int(''.join(random.choice('123456789') for _ in range(6))))
        kwargs.setdefault('exten', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        kwargs.setdefault('supervision', 0)
        kwargs.setdefault('label', 'toto')
        kwargs.setdefault('typeextenumbersright', 'user')
        kwargs.setdefault('typeextenumbers', None)
        kwargs.setdefault('typevalextenumbers', None)
        kwargs.setdefault('progfunckey', '1')

        phone_func_key = PhoneFunckey(**kwargs)
        self.add_me(phone_func_key)
        return phone_func_key

    def add_sccp_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('option_name', 'directmedia')
        kwargs.setdefault('option_value', 'no')

        sccp_general_settings = SCCPGeneralSettings(**kwargs)
        self.add_me(sccp_general_settings)
        return sccp_general_settings

    def add_cel(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('eventtype', 'eventtype')
        kwargs.setdefault('eventtime', datetime.datetime.now())
        kwargs.setdefault('userdeftype', 'userdeftype')
        kwargs.setdefault('cid_name', 'cid_name')
        kwargs.setdefault('cid_num', 'cid_num')
        kwargs.setdefault('cid_ani', 'cid_ani')
        kwargs.setdefault('cid_rdnis', 'cid_rdnis')
        kwargs.setdefault('cid_dnid', 'cid_dnid')
        kwargs.setdefault('exten', 'exten')
        kwargs.setdefault('context', 'context')
        kwargs.setdefault('channame', 'channame')
        kwargs.setdefault('appname', 'appname')
        kwargs.setdefault('appdata', 'appdata')
        kwargs.setdefault('amaflags', 0)
        kwargs.setdefault('accountcode', 'accountcode')
        kwargs.setdefault('peeraccount', 'peeraccount')
        kwargs.setdefault('uniqueid', 'uniqueid')
        kwargs.setdefault('linkedid', 'linkedid')
        kwargs.setdefault('userfield', 'userfield')
        kwargs.setdefault('peer', 'peer')

        cel = CELSchema(**kwargs)
        self.add_me(cel)
        return cel.id

    def add_voicemail(self, **kwargs):
        kwargs.setdefault('fullname', 'Auto Voicemail')
        kwargs.setdefault('mailbox', ''.join(random.choice('0123456789_*X.') for _ in range(6)))
        kwargs.setdefault('context', 'unittest')
        kwargs.setdefault('uniqueid', self._generate_int())

        voicemail = VoicemailSchema(**kwargs)
        self.add_me(voicemail)
        return voicemail

    def link_user_and_voicemail(self, user_row, voicemail_id):
        user_row.voicemailtype = 'asterisk'
        user_row.voicemailid = voicemail_id

        if not user_row.language:
            user_row.language = 'fr_FR'

        self.add_me(user_row)

    def add_musiconhold(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'musiconhold.conf')
        kwargs.setdefault('category', 'default')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        musiconhold = MusicOnHold(**kwargs)
        self.add_me(musiconhold)
        return musiconhold

    def add_meetme_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'meetme.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_meetme = StaticMeetme(**kwargs)
        self.add_me(static_meetme)
        return static_meetme

    def add_voicemail_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'voicemail.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_voicemail = StaticVoicemail(**kwargs)
        self.add_me(static_voicemail)
        return static_voicemail

    def add_iax_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'sip.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_iax = StaticIAX(**kwargs)
        self.add_me(static_iax)
        return static_iax

    def add_sip_general_settings(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('cat_metric', 0)
        kwargs.setdefault('var_metric', 0)
        kwargs.setdefault('commented', 0)
        kwargs.setdefault('filename', 'sip.conf')
        kwargs.setdefault('category', 'general')
        kwargs.setdefault('var_name', self._random_name())
        kwargs.setdefault('var_val', self._random_name())

        static_sip = StaticSIP(**kwargs)
        self.add_me(static_sip)
        return static_sip

    def add_sip_authentication(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('usersip_id', self._generate_int())
        kwargs.setdefault('user', self._random_name())
        kwargs.setdefault('secretmode', 'md5')
        kwargs.setdefault('secret', self._random_name())
        kwargs.setdefault('realm', self._random_name())

        sip_authentication = SIPAuthentication(**kwargs)
        self.add_me(sip_authentication)
        return sip_authentication

    def add_func_key(self, **kwargs):
        func_key_row = FuncKey(**kwargs)
        self.add_me(func_key_row)
        return func_key_row

    def add_func_key_template(self, **kwargs):
        func_key_template = FuncKeyTemplate(**kwargs)
        self.add_me(func_key_template)
        return func_key_template

    def add_func_key_type(self, **kwargs):
        kwargs.setdefault('id', self._generate_int())
        kwargs.setdefault('name', 'speeddial')
        func_key_type_row = FuncKeyType(**kwargs)
        self.add_me(func_key_type_row)
        return func_key_type_row

    def add_func_key_destination_type(self, **kwargs):
        kwargs.setdefault('id', 1)
        kwargs.setdefault('name', 'user')
        destination_type_row = FuncKeyDestinationType(**kwargs)
        self.add_me(destination_type_row)
        return destination_type_row

    def add_entity(self, **kwargs):
        kwargs.setdefault('name', 'entity')
        kwargs.setdefault('displayname', 'entity')
        kwargs.setdefault('description', '')
        entity = EntitySchema(**kwargs)

        self.add_me(entity)

        return entity

    def add_bsfilter(self, **kwargs):
        options = {'callfrom': 'internal',
                   'type': 'bosssecretary',
                   'bosssecretary': 'bossfirst-serial',
                   'name': 'bsfilter',
                   'description': '',
                   'commented': 0}
        options.update(kwargs)

        callfilter = Callfilter(**options)
        self.add_me(callfilter)
        return callfilter

    def add_filter_member(self, filterid, userid, role='boss'):
        member = Callfiltermember(type='user',
                                  typeval=str(userid),
                                  callfilterid=filterid,
                                  bstype=role)
        self.add_me(member)
        return member

    def add_func_key_mapping(self, **kwargs):
        func_key_mapping = FuncKeyMapping(**kwargs)
        self.add_me(func_key_mapping)
        return func_key_mapping

    def add_features(self, **kwargs):
        kwargs.setdefault('filename', 'features.conf')
        kwargs.setdefault('category', 'general')
        feature = Features(**kwargs)
        self.add_me(feature)
        return feature

    def add_paging(self, **kwargs):
        kwargs.setdefault('number', '1234')
        kwargs.setdefault('timeout', 30)
        paging = Paging(**kwargs)
        self.add_me(paging)
        return paging

    def add_accessfeatures(self, host, **kwargs):
        kwargs.setdefault('feature', 'phonebook')
        accessfeature = AccessFeatures(host=host, **kwargs)
        self.add_me(accessfeature)
        return accessfeature

    def add_infos(self):
        infos = Infos()
        self.add_me(infos)
        return infos

    def add_me(self, obj):
        self.session.add(obj)
        self.session.flush()

    def add_me_all(self, obj_list):
        self.session.add_all(obj_list)
        self.session.flush()

    _generate_int = itertools.count(1).next

    def _random_name(self, length=6):
        return ''.join(random.choice(string.lowercase) for _ in range(length))
