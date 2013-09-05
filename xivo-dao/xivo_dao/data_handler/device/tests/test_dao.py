# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from hamcrest import *
from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.devicefeatures import DeviceFeatures as DeviceSchema
from xivo_dao.data_handler.device.model import Device
from mock import Mock, patch
from xivo_dao.data_handler.exception import ElementDeletionError, ElementCreationError


class TestDeviceDao(DAOTestCase):

    tables = [
        DeviceSchema
    ]

    def _has_properties(self, properties):
        matchers = []
        for key, value in properties.iteritems():
            matchers.append(has_property(key, value))
        return all_of(*matchers)

    def setUp(self):
        self.empty_tables()

    def test_get_no_device(self):
        self.assertRaises(LookupError, device_dao.get, '666')

    def test_get(self):
        deviceid = 'sdklfj'

        expected_device = self.add_device(deviceid=deviceid)

        device = device_dao.get(expected_device.id)

        assert_that(device.deviceid, equal_to(deviceid))

    def test_get_by_deviceid_no_device(self):
        self.assertRaises(LookupError, device_dao.get_by_deviceid, '1234')

    def test_get_by_deviceid(self):
        deviceid = 'sdklfj'

        expected_device = self.add_device(deviceid=deviceid)

        device = device_dao.get_by_deviceid(deviceid)

        assert_that(device.id, equal_to(expected_device.id))
        assert_that(device.deviceid, equal_to(deviceid))

    def test_find_not_found(self):
        device_id = 39784

        result = device_dao.find(device_id)

        assert_that(result, none())

    def test_find_found(self):
        device_id = 39784
        device_row = self.add_device(deviceid=device_id)
        expected_device = Device.from_data_source(device_row)

        result = device_dao.find(expected_device.id)

        assert_that(result, equal_to(expected_device))

    def test_find_all_no_devices(self):
        expected = []

        result = device_dao.find_all()

        assert_that(result, equal_to(expected))

    def test_find_all(self):
        device1 = {
            'deviceid': 'deviceid1',
            'config': 'config1',
            'plugin': 'plugin1',
            'ip': 'ip1',
            'mac': 'mac1',
            'sn': 'sn1',
            'vendor': 'vendor1',
            'model': 'model1',
            'version': 'version1',
            'proto': 'proto1',
            'internal': 1,
            'configured': 1,
            'commented': 1,
            'description': 'description1'
        }
        device2 = {
            'deviceid': 'deviceid2',
            'config': 'config2',
            'plugin': 'plugin2',
            'ip': 'ip2',
            'mac': 'mac2',
            'sn': 'sn2',
            'vendor': 'vendor2',
            'model': 'model2',
            'version': 'version2',
            'proto': 'proto2',
            'internal': 2,
            'configured': 2,
            'commented': 2,
            'description': 'description2'
        }
        self.add_device(**device1)
        self.add_device(**device2)

        result = device_dao.find_all()

        assert_that(result, has_items(
            self._has_properties(device1),
            self._has_properties(device2),
        ))

    def test_create(self):

        device_properties = {
            'deviceid': 'deviceid1',
            'config': 'config1',
            'plugin': 'plugin1',
            'ip': 'ip1',
            'mac': 'mac1',
            'sn': 'sn1',
            'vendor': 'vendor1',
            'model': 'model1',
            'version': 'version1',
            'proto': 'proto1',
            'internal': 1,
            'configured': 1,
            'commented': 1,
            'description': 'description1'
        }

        device = Device(**device_properties)

        result = device_dao.create(device)

        assert_that(result, self._has_properties(device_properties))
        assert_that(result, has_property('id', instance_of(int)))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_with_error_from_dao(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        extension = Device(deviceid='toto')

        self.assertRaises(ElementCreationError, device_dao.create, extension)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete(self):
        deviceid = 'sdklfj'
        expected_extension = self.add_device(deviceid=deviceid)

        extension = device_dao.get(expected_extension.id)

        device_dao.delete(extension)

        row = self.session.query(DeviceSchema).filter(DeviceSchema.id == expected_extension.id).first()

        self.assertEquals(row, None)

    def test_delete_not_exist(self):
        extension = Device(id=1)

        self.assertRaises(ElementDeletionError, device_dao.delete, extension)

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_mac_exists_no_mac(self, mock_device_manager):
        device_manager = Mock()
        mock_device_manager.return_value = device_manager
        device_manager.find.return_value = []

        mac = 'FF:FF:FF:FF:FF'

        result = device_dao.mac_exists(mac)

        assert_that(result, equal_to(False))
        device_manager.find.assert_called_once_with({'mac': mac})

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_mac_exists_with_a_mac(self, mock_device_manager):
        device_manager = Mock()
        mock_device_manager.return_value = device_manager
        device_manager.find.return_value = [{u'added': u'auto',
                                             u'config': u'cb20ee7c27e2483ba737e8061b40113d',
                                             u'configured': True,
                                             u'id': u'cb20ee7c27e2483ba737e8061b40113d',
                                             u'ip': u'10.0.0.1',
                                             u'mac': u'FF:FF:FF:FF:FF:FF',
                                             u'model': u'820',
                                             u'plugin': u'xivo-snom-8.7.3.19',
                                             u'vendor': u'Snom',
                                             u'version': u'8.7.3.19'}]

        mac = 'FF:FF:FF:FF:FF'

        result = device_dao.mac_exists(mac)

        assert_that(result, equal_to(True))
        device_manager.find.assert_called_once_with({'mac': mac})

    @patch('xivo_dao.helpers.provd_connector.plugin_manager')
    def test_plugin_exists_no_plugin(self, mock_plugin_manager):
        plugin_manager = Mock()
        mock_plugin_manager.return_value = plugin_manager
        plugin_manager.installed.return_value = {}

        plugin = 'null'

        result = device_dao.plugin_exists(plugin)

        assert_that(result, equal_to(False))
        plugin_manager.installed.assert_called_once_with(plugin)

    @patch('xivo_dao.helpers.provd_connector.plugin_manager')
    def test_plugin_exists_with_a_plugin_installed(self, mock_plugin_manager):
        plugin_manager = Mock()
        mock_plugin_manager.return_value = plugin_manager
        plugin_manager.installed.return_value = {
            u'null': {u'capabilities': {u'*, *, *': {u'sip.lines': 0}},
            u'description': u'Plugin that offers no configuration service and rejects TFTP/HTTP requests.',
            u'version': u'1.0-a'}}

        plugin = 'null'

        result = device_dao.plugin_exists(plugin)

        assert_that(result, equal_to(True))
        plugin_manager.installed.assert_called_once_with(plugin)

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_template_id_exists_no_template(self, mock_config_manager):
        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        config_manager.find.return_value = []

        template_id = 'abcd1234'

        result = device_dao.template_id_exists(template_id)

        assert_that(result, equal_to(False))
        config_manager.find.assert_called_once_with({'X_type': 'device', 'id': template_id})

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_template_id_exists_with_a_template(self, mock_config_manager):
        config_manager = Mock()
        mock_config_manager.return_value = config_manager

        template_id = 'abcd1234'

        config_manager.find.return_value = [{
            u'X_type': u'device',
            u'deletable': True,
            u'id': template_id,
            u'label': u'testtemplate',
            u'parent_ids': [],
            u'raw_config': {}}]

        result = device_dao.template_id_exists(template_id)

        assert_that(result, equal_to(True))
        config_manager.find.assert_called_once_with({'X_type': 'device', 'id': template_id})
