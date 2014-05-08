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

import copy
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from xivo_dao import record_campaigns_dao
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.alchemy.recordings import Recordings
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.tests.test_preriquisites import recording_preriquisites


class TestRecordCampaignDao(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        recording_preriquisites(self.session)
        self._create_sample_campaign()

    def test_get_records(self):
        campaign = copy.deepcopy(self.sample_campaign)

        self.session.begin()
        self.session.add(campaign)
        self.session.commit()

        paginator = (1, 1)
        (total, items) = record_campaigns_dao.get_records(search=None,
                                                          checkCurrentlyRunning=False,
                                                          paginator=paginator)
        self.assertEquals([campaign], items)
        self.assertEqual(total, 1)

    def test_id_from_name(self):
        campaign = copy.deepcopy(self.sample_campaign)

        self.session.begin()
        self.session.add(campaign)
        self.session.commit()

        retrieved_id = record_campaigns_dao.id_from_name(campaign.campaign_name)
        self.assertEquals(retrieved_id, campaign.id)
        self.assertEqual(None, record_campaigns_dao.id_from_name('test'))

    def test_add(self):
        campaign = copy.deepcopy(self.sample_campaign)
        gen_id = record_campaigns_dao.add_or_update(campaign)
        self.assertTrue(gen_id > 0)
        result = self.session.query(RecordCampaigns).all()
        self.assertEqual([campaign], result)

    def test_update(self):
        campaign = copy.deepcopy(self.sample_campaign)

        self.session.begin()
        self.session.add(campaign)
        self.session.commit()

        new_name = campaign.campaign_name + "1"
        new_queue_id = 2
        campaign.campaign_name = new_name
        campaign.queue_id = new_queue_id
        record_campaigns_dao.add_or_update(campaign)

        result = self.session.query(RecordCampaigns).all()
        self.assertEquals(len(result), 1)
        updated_campaign = result[0]
        self.assertEqual(updated_campaign.campaign_name,
                         new_name)
        self.assertEqual(updated_campaign.queue_id,
                         new_queue_id)

    def test_get(self):
        campaign = copy.deepcopy(self.sample_campaign)

        self.session.begin()
        self.session.add(campaign)
        self.session.commit()

        returned_obj = record_campaigns_dao.get(campaign.id)
        self.assertEqual(returned_obj, campaign)

    def test_delete(self):
        campaign = copy.deepcopy(self.sample_campaign)

        self.session.begin()
        self.session.add(campaign)
        self.session.commit()

        record_campaigns_dao.delete(campaign)
        self.assertEqual(None, record_campaigns_dao.get(campaign.id))

    def test_delete_integrity_error(self):
        campaign = copy.deepcopy(self.sample_campaign)

        self.session.begin()
        self.session.add(campaign)
        self.session.commit()

        recording = Recordings()
        recording.campaign_id = campaign.id
        recording.filename = 'file'
        recording.cid = '123'
        recording.agent_id = 1
        recording.caller = '2002'

        self.session.begin()
        self.session.add(recording)
        self.session.commit()

        self.assertRaises(IntegrityError,
                          record_campaigns_dao.delete,
                          campaign)

    def test_delete_all(self):
        campaign1 = copy.deepcopy(self.sample_campaign1)
        campaign2 = copy.deepcopy(self.sample_campaign2)

        self.session.begin()
        self.session.add_all([campaign1, campaign2])
        self.session.commit()

        id1, id2 = campaign1.id, campaign2.id
        record_campaigns_dao.delete_all()
        self.assertEqual(None, record_campaigns_dao.get(id1))
        self.assertEqual(None, record_campaigns_dao.get(id2))

    def test_delete_all_integrity_error(self):
        campaign1 = copy.deepcopy(self.sample_campaign1)
        campaign2 = copy.deepcopy(self.sample_campaign2)

        self.session.begin()
        self.session.add_all([campaign1, campaign2])
        self.session.commit()

        id1, id2 = campaign1.id, campaign2.id

        recording = Recordings()
        recording.campaign_id = campaign1.id
        recording.filename = 'file'
        recording.cid = '123'
        recording.agent_id = 1
        recording.caller = '2002'

        self.session.begin()
        self.session.add(recording)
        self.session.commit()

        self.assertRaises(IntegrityError, record_campaigns_dao.delete_all)
        self.assertNotEqual(None, record_campaigns_dao.get(id1))
        self.assertNotEqual(None, record_campaigns_dao.get(id2))

    def _create_sample_campaign(self):
        self.sample_campaign = RecordCampaigns()
        self.sample_campaign.activated = True
        self.sample_campaign.campaign_name = "campaign-àé"
        self.sample_campaign.queue_id = 1
        self.sample_campaign.base_filename = self.sample_campaign.campaign_name + "-"
        self.sample_campaign.start_date = datetime.strptime('2012-01-01 12:12:12',
                                                            '%Y-%m-%d %H:%M:%S')
        self.sample_campaign.end_date = datetime.strptime('2012-12-12 12:12:12',
                                                          '%Y-%m-%d %H:%M:%S')
        self.sample_campaign1 = RecordCampaigns()
        self.sample_campaign1.activated = True
        self.sample_campaign1.campaign_name = "campaign1-àé"
        self.sample_campaign1.queue_id = 1
        self.sample_campaign1.base_filename = self.sample_campaign.campaign_name + "-"
        self.sample_campaign1.start_date = datetime.strptime('2012-01-01 12:12:12',
                                                            '%Y-%m-%d %H:%M:%S')
        self.sample_campaign1.end_date = datetime.strptime('2012-12-12 12:12:12',
                                                          '%Y-%m-%d %H:%M:%S')
        self.sample_campaign2 = RecordCampaigns()
        self.sample_campaign2.activated = True
        self.sample_campaign2.campaign_name = "campaign2-àé"
        self.sample_campaign2.queue_id = 1
        self.sample_campaign2.base_filename = self.sample_campaign.campaign_name + "-"
        self.sample_campaign2.start_date = datetime.strptime('2012-01-01 12:12:12',
                                                            '%Y-%m-%d %H:%M:%S')
        self.sample_campaign2.end_date = datetime.strptime('2012-12-12 12:12:12',
                                                          '%Y-%m-%d %H:%M:%S')
