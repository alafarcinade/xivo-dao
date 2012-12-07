# -*- coding: utf-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
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

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao import userfeatures_dao


class TestUserFeaturesDAO(DAOTestCase):

    tables = [UserFeatures, LineFeatures, ContextInclude, AgentFeatures,
              CtiPresences, CtiPhoneHintsGroup, CtiProfile]

    def setUp(self):
        self.empty_tables()

    def test_get_one_result(self):
        user_id = self._insert_user('first')

        user = userfeatures_dao.get(user_id)

        self.assertEqual(user.id, user_id)

    def test_get_string_id(self):
        user_id = self._insert_user('first')

        user = userfeatures_dao.get(str(user_id))

        self.assertEqual(user.id, user_id)

    def test_get_no_result(self):
        self.assertRaises(LookupError, userfeatures_dao.get, 1)

    def _insert_user(self, firstname):
        user = UserFeatures()
        user.firstname = firstname
        self.session.add(user)
        self.session.commit()
        return user.id

    def test_find_by_agent_id(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.session.add(user)
        self.session.commit()

        user_ids = userfeatures_dao.find_by_agent_id(agent_id)

        self.assertEqual(user_ids[0], user.id)

    def test_agent_id(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.session.add(user)
        self.session.commit()

        res = userfeatures_dao.agent_id(user.id)

        self.assertEqual(res, agent_id)

    def test_agent_id_no_agent(self):
        user = UserFeatures()

        user.firstname = 'test_agent'

        self.session.add(user)
        self.session.commit()

        res = userfeatures_dao.agent_id(user.id)

        self.assertEqual(res, None)

    def test_is_agent_yes(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.is_agent(user.id)

        self.assertEqual(result, True)

    def test_is_agent_no(self):
        user = UserFeatures()

        user.firstname = 'test_agent'

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.is_agent(user.id)

        self.assertEqual(result, False)

    def test_get_profile(self):
        user_profile_id = self._add_profile('test_profile')

        user = UserFeatures()
        user.firstname = 'test_agent'
        user.cti_profile_id = user_profile_id
        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_profile(user.id)

        self.assertEqual(result, user_profile_id)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name
        self.session.add(cti_presence)
        self.session.commit()
        return cti_presence.id

    def _add_phone_hints_group(self, name):
        cti_phone_hints_group = CtiPhoneHintsGroup()
        cti_phone_hints_group.name = name
        self.session.add(cti_phone_hints_group)
        self.session.commit()
        return cti_phone_hints_group.id

    def _add_profile(self, name):
        cti_profile = CtiProfile()
        cti_profile.name = name
        cti_profile.presence_id = self._add_presence('test_presence')
        cti_profile.phonehints_id = self._add_phone_hints_group('test_add_phone_hints_group')
        self.session.add(cti_profile)
        self.session.commit()
        return cti_profile.id

    def _add_user_with_line(self, name, context):
        user = UserFeatures()
        user.firstname = name

        self.session.add(user)
        self.session.commit()

        line = LineFeatures()
        line.iduserfeatures = user.id
        line.context = context
        line.protocolid = 1
        line.name = 'jk1j3'
        line.provisioningid = '12345'

        self.session.add(line)
        self.session.commit()

        return user

    def test_get_reachable_contexts(self):
        context = 'my_context'

        user = self._add_user_with_line('Tester', context)

        result = userfeatures_dao.get_reachable_contexts(user.id)

        self.assertEqual(result, [context])

    def test_get_reachable_context_no_line(self):
        user = UserFeatures()
        user.name = 'Tester'

        self.session.add(user)
        self.session.commit()

        self.assertEqual(userfeatures_dao.get_reachable_contexts(user.id), [])

    def test_get_reachable_context_included_ctx(self):
        context = 'my_context'
        included_context = 'second_ctx'

        ctx_include = ContextInclude()
        ctx_include.context = context
        ctx_include.include = included_context

        self.session.add(ctx_include)
        self.session.commit()

        user = self._add_user_with_line('Tester', context)

        result = userfeatures_dao.get_reachable_contexts(user.id)

        self.assertEqual(result, [context, included_context])

    def test_get_reachable_context_loop(self):
        context = 'my_context'
        included_context = 'second_ctx'
        looping_context = 'third_ctx'

        ctx = ContextInclude()
        ctx.context = context
        ctx.include = included_context

        ctx_include = ContextInclude()
        ctx_include.context = included_context
        ctx_include.include = looping_context

        ctx_loop = ContextInclude()
        ctx_loop.context = looping_context
        ctx_loop.include = context

        map(self.session.add, [ctx, ctx_include, ctx_loop])
        self.session.commit()

        user = self._add_user_with_line('Tester', context)

        result = userfeatures_dao.get_reachable_contexts(user.id)

        for context in [context, included_context, looping_context]:
            self.assertTrue(context in result)

    def test_get_line_identity(self):
        self.assertRaises(LookupError, userfeatures_dao.get_line_identity, 1234)

        user = UserFeatures()
        user.name = 'Tester'

        self.session.add(user)
        self.session.commit()

        line = LineFeatures()
        line.protocolid = 1
        line.name = 'a1b2c3'
        line.protocol = 'sip'
        line.iduserfeatures = user.id
        line.context = 'ctx'
        line.provisioningid = 1234

        self.session.add(line)
        self.session.commit()

        expected = 'sip/a1b2c3'
        result = userfeatures_dao.get_line_identity(user.id)

        self.assertEqual(result, expected)

    def test_find_by_line_id(self):
        user = UserFeatures()
        user.firstname = 'test'

        self.session.add(user)
        self.session.commit()

        line = LineFeatures()
        line.protocolid = 1
        line.name = 'abc'
        line.context = 'test_ctx'
        line.provisioningid = 2
        line.iduserfeatures = user.id

        self.session.add(line)
        self.session.commit()

        user_id = userfeatures_dao.find_by_line_id(line.id)

        self.assertEqual(user_id, user.id)

    def test_get_agent_number(self):
        self.assertRaises(LookupError, userfeatures_dao.get_agent_number, 1)

        agent = AgentFeatures()
        agent.number = '1234'
        agent.numgroup = 0
        agent.passwd = ''
        agent.context = 'ctx'
        agent.language = 'fr'

        self.session.add(agent)
        self.session.commit()

        user = UserFeatures()
        user.agentid = agent.id

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_agent_number(user.id)

        self.assertEqual(result, agent.number)

    def test_get_dest_unc(self):
        user = UserFeatures()

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_dest_unc(user.id)

        self.assertEqual(result, '')

        user.destunc = '1002'

        self.session.commit()

        result = userfeatures_dao.get_dest_unc(user.id)

        self.assertEqual(result, '1002')

    def test_get_fwd_unc(self):
        user = UserFeatures()

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_fwd_unc(user.id)

        self.assertFalse(result)

        user.enableunc = 1

        self.session.commit()

        result = userfeatures_dao.get_fwd_unc(user.id)

        self.assertTrue(result)

    def test_get_dest_busy(self):
        user = UserFeatures()

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_dest_busy(user.id)

        self.assertEqual(result, '')

        user.destbusy = '1002'

        self.session.commit()

        result = userfeatures_dao.get_dest_busy(user.id)

        self.assertEqual(result, '1002')

    def test_get_fwd_busy(self):
        user = UserFeatures()

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_fwd_busy(user.id)

        self.assertFalse(result)

        user.enablebusy = 1

        self.session.commit()

        result = userfeatures_dao.get_fwd_busy(user.id)

        self.assertTrue(result)

    def test_get_dest_rna(self):
        user = UserFeatures()

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_dest_rna(user.id)

        self.assertEqual(result, '')

        user.destrna = '1002'

        self.session.commit()

        result = userfeatures_dao.get_dest_rna(user.id)

        self.assertEqual(result, '1002')

    def test_get_fwd_rna(self):
        user = UserFeatures()

        self.session.add(user)
        self.session.commit()

        result = userfeatures_dao.get_fwd_rna(user.id)

        self.assertFalse(result)

        user.enablerna = 1

        self.session.commit()

        result = userfeatures_dao.get_fwd_rna(user.id)

        self.assertTrue(result)

    def test_get_name_number(self):
        user = UserFeatures()
        user.firstname = 'Toto'
        user.lastname = 'Plop'

        self.session.add(user)
        self.session.commit()

        line = LineFeatures()
        line.number = '1234'
        line.name = '12kjdhf'
        line.context = 'context'
        line.provisioningid = 1234
        line.iduserfeatures = user.id
        line.protocolid = 1

        self.session.add(line)
        self.session.commit()

        name, number = userfeatures_dao.get_name_number(user.id)

        self.assertEqual(name, '%s %s' % (user.firstname, user.lastname))
        self.assertEqual(number, '1234')

    def test_get_device_id_with_one_user(self):
        device_id = 8

        user = UserFeatures()
        user.firstname = 'Toto'
        user.lastname = 'Plop'

        self.session.add(user)
        self.session.commit()

        line = LineFeatures()
        line.number = '1234'
        line.name = '12kjdhf'
        line.context = 'context'
        line.provisioningid = 1234
        line.iduserfeatures = user.id
        line.protocolid = 1
        line.device = str(8)

        self.session.add(line)
        self.session.commit()

        result = userfeatures_dao.get_device_id(user.id)

        self.assertEqual(result, device_id)

    def test_get_device_id_with_two_users(self):
        device_id = 24

        user1 = UserFeatures()
        user1.firstname = 'Toto1'
        user1.lastname = 'Plop1'

        self.session.add(user1)

        user2 = UserFeatures()
        user2.firstname = 'Toto2'
        user2.lastname = 'Plop2'

        self.session.add(user2)
        self.session.commit()

        line = LineFeatures()
        line.number = '1234'
        line.name = '12kjdhf'
        line.context = 'context'
        line.provisioningid = 1234
        line.iduserfeatures = user2.id
        line.protocolid = 1
        line.device = str(device_id)

        self.session.add(line)
        self.session.commit()

        result = userfeatures_dao.get_device_id(user2.id)

        self.assertEqual(result, device_id)

    def test_get_device_id_no_line(self):
        user = UserFeatures()
        user.firstname = 'Toto'
        user.lastname = 'Plop'

        self.session.add(user)
        self.session.commit()

        self.assertRaises(LookupError, userfeatures_dao.get_device_id, user.id)

    def test_get_device_id_no_user(self):
        self.assertRaises(LookupError, userfeatures_dao.get_device_id, 666)
