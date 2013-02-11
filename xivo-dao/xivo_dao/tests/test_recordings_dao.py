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
from xivo_dao import recordings_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.alchemy.recordings import Recordings
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.tests.test_preriquisites import recording_preriquisites
import copy


class TestRecordingDao(DAOTestCase):

    tables = [QueueFeatures, AgentFeatures, Recordings, RecordCampaigns]

    def setUp(self):
        self.empty_tables()
        recording_preriquisites(self.session)
        self._insert_campaign()
        self._create_sample_recording()

    def test_get_recordings(self):
        my_recording1 = copy.deepcopy(self.sample_recording)
        my_recording2 = copy.deepcopy(self.sample_recording)
        my_recording2.cid = '002'
        my_recording2.caller = '3003'
        self.session.add(my_recording1)
        self.session.add(my_recording2)
        print "1: ", my_recording1
        print "2: ", my_recording2
        print "default: ", self.sample_recording
        self.session.commit()

        search = {'caller': '2002'}
        paginator = (1, 1)
        (total, items) = recordings_dao\
                     .get_recordings(self.campaign.id, search, paginator)
        self.assertEqual(total, 1)
        self.assertEquals(items, [my_recording1])

    def test_add_recording(self):
        my_recording = copy.deepcopy(self.sample_recording)
        recordings_dao.add_recording(my_recording)
        result = self.session.query(Recordings).all()
        self.assertEqual([my_recording], result)

    def test_search_recordings(self):
        my_recording1 = copy.deepcopy(self.sample_recording)
        my_recording2 = copy.deepcopy(self.sample_recording)
        my_recording2.cid = '002'
        my_recording2.caller = '3003'
        self.session.add(my_recording1)
        self.session.add(my_recording2)
        self.session.commit()

        key = '3003'
        paginator = (1, 2)
        (total, items) = recordings_dao\
                     .search_recordings(self.campaign.id, key, paginator)
        self.assertEqual(total, 1)
        self.assertEquals([my_recording2], items)

        key = '1000'
        (total, items) = recordings_dao\
                     .search_recordings(self.campaign.id, key, paginator)
        self.assertEquals(total, 2)
        self.assertEquals(items, [my_recording1, my_recording2])

    def test_delete(self):
        result = recordings_dao.delete(1, '001')
        self.assertEquals(result, None)
        my_recording = copy.deepcopy(self.sample_recording)
        self.session.add(my_recording)
        self.session.commit()

        data = self.session.query(Recordings).all()
        self.assertEqual([my_recording], data)
        result = recordings_dao.delete(self.campaign.id,
                                                  my_recording.cid)
        data = self.session.query(Recordings).all()
        self.assertEquals(data, [])
        self.assertEquals(result, my_recording.filename)

    def _insert_campaign(self):
        self.campaign = RecordCampaigns()
        self.campaign.campaign_name = 'name'
        self.campaign.base_filename = 'file-'
        self.campaign.queue_id = 1
        self.campaign.start_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.end_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.activated = True
        self.session.add(self.campaign)
        self.session.commit()

    def _create_sample_recording(self):
        self.sample_recording = Recordings()
        self.sample_recording.cid = '001'
        self.sample_recording.caller = '2002'
        self.sample_recording.callee = ''
        self.sample_recording.agent_id = 1
        self.sample_recording.filename = 'file.wav'
        self.sample_recording.start_time = datetime.strptime('2012-01-01 00:00:00',
                                                      "%Y-%m-%d %H:%M:%S")
        self.sample_recording.end_time = datetime.strptime('2012-01-01 00:10:00',
                                                      "%Y-%m-%d %H:%M:%S")
        self.sample_recording.campaign_id = self.campaign.id
        self.sample_recording.client_id = ''
