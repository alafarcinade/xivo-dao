# -*- coding: utf-8 -*-

import unittest

from hamcrest import assert_that, equal_to
from mock import patch, Mock
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.user_line_extension import services as user_line_extension_services
from xivo_dao.data_handler.exception import InvalidParametersError, ElementCreationError, ElementDeletionError
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.extension.model import Extension


class TestUserLineExtensionServices(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_user_id', Mock(return_value=[]))
    def test_find_all_by_user_id_not_found(self):
        expected_result = []
        user_id = 39847

        result = user_line_extension_services.find_all_by_user_id(user_id)

        assert_that(expected_result, equal_to(result))

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_user_id')
    def test_find_all_by_user_id_found(self, mock_dao):
        user_id = 39847
        user_line_extension = UserLineExtension(user_id=user_id, line_id=1234, extension_id=4343)
        mock_dao.return_value = user_line_extension

        result = user_line_extension_services.find_all_by_user_id(user_id)

        assert_that(result, equal_to(user_line_extension))

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_extension_id', Mock(return_value=[]))
    def test_find_all_by_extension_id_not_found(self):
        expected_result = []
        extension_id = 39847

        result = user_line_extension_services.find_all_by_extension_id(extension_id)

        assert_that(expected_result, equal_to(result))

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_extension_id')
    def test_find_all_by_extension_id_found(self, mock_dao):
        extension_id = 39847
        user_line_extension = UserLineExtension(user_id=extension_id, line_id=1234, extension_id=4343)
        mock_dao.return_value = user_line_extension

        result = user_line_extension_services.find_all_by_extension_id(extension_id)

        assert_that(result, equal_to(user_line_extension))

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_line_id', Mock(return_value=[]))
    def test_find_all_by_line_id_not_found(self):
        expected_result = []
        line_id = 39847

        result = user_line_extension_services.find_all_by_line_id(line_id)

        assert_that(expected_result, equal_to(result))

    @patch('xivo_dao.data_handler.user_line_extension.dao.find_all_by_line_id')
    def test_find_all_by_line_id_found(self, mock_dao):
        line_id = 39847
        user_line_extension = UserLineExtension(user_id=1324, line_id=line_id, extension_id=4343)
        mock_dao.return_value = user_line_extension

        result = user_line_extension_services.find_all_by_line_id(line_id)

        assert_that(result, equal_to(user_line_extension))

    @patch('xivo_dao.data_handler.user_line_extension.validator.validate')
    def test_create_with_invalid_ule(self, ule_validate):
        user_line_extension = UserLineExtension()

        ule_validate.side_effect = InvalidParametersError('')

        self.assertRaises(InvalidParametersError, user_line_extension_services.create, user_line_extension)

    @patch('xivo_dao.data_handler.user_line_extension.validator.validate')
    @patch('xivo_dao.data_handler.user_line_extension.notifier.created')
    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    @patch('xivo_dao.data_handler.line.dao.edit')
    @patch('xivo_dao.data_handler.extension.dao.edit')
    def test_create(self,
                    extension_edit,
                    line_edit,
                    user_line_extension_dao_create,
                    user_line_extension_notifier_created,
                    ule_validate):

        exten = '1000'
        context = 'default'
        ule_id = 63
        line_id = 52
        user_id = 5898
        extension_id = 52
        callerid = 'Francis Dagobert'

        ule = UserLineExtension(user_id=user_id,
                                line_id=line_id,
                                extension_id=extension_id,
                                main_user=True,
                                main_line=False)
        user = User(id=user_id,
                    callerid=callerid)

        line = LineSIP(id=line_id,
                       callerid=callerid,
                       number=exten,
                       context=context)

        extension = Extension(id=extension_id,
                              exten=exten,
                              context=context)

        def mock_dao(ule):
            ule.id = ule_id
            return ule

        user_line_extension_dao_create.side_effect = mock_dao

        ule_validate.return_value = (user, line, extension)

        result = user_line_extension_services.create(ule)

        ule_validate.assert_called_once_with(ule)
        user_line_extension_dao_create.assert_called_once_with(ule)
        self.assertEquals(type(result), UserLineExtension)
        self.assertEquals(result.id, ule_id)
        self.assertEquals(extension.type, 'user')
        self.assertEquals(extension.typeval, str(user_id))
        extension_edit.assert_called_once_with(extension)
        line_edit.assert_called_once_with(line)
        user_line_extension_notifier_created.assert_called_once_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.dao.create')
    @patch('xivo_dao.data_handler.user_line_extension.validator.validate')
    def test_create_with_error_from_dao(self, user_line_extension_dao_create, ule_validate):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        ule_validate.return_value = (Mock(), Mock(), Mock())

        error = Exception("message")
        user_line_extension_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, user_line_extension_services.create, ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.edited')
    @patch('xivo_dao.data_handler.user_line_extension.dao.edit')
    @patch('xivo_dao.data_handler.user_line_extension.validator.validate')
    def test_edit(self, user_dao_edit, user_notifier_edited, ule_validate):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        ule_validate.return_value = (Mock(), Mock(), Mock())

        user_line_extension_services.edit(ule)

        ule_validate.assert_called_once_with(ule)
        user_dao_edit.assert_called_once_with(ule)
        user_notifier_edited.assert_called_once_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.validator.validate_delete')
    @patch('xivo_dao.data_handler.user_line_extension.notifier.deleted')
    @patch('xivo_dao.data_handler.user_line_extension.dao.delete')
    def test_delete(self, user_line_extension_dao_delete, user_line_extension_notifier_deleted, ule_validate):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        ule_validate.return_value = (Mock(), Mock(), Mock())

        user_line_extension_services.delete(ule)

        ule_validate.assert_called_once_with(ule)
        user_line_extension_dao_delete.assert_called_once_with(ule)
        user_line_extension_notifier_deleted.assert_called_once_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.deleted')
    @patch('xivo_dao.data_handler.user_line_extension.dao.delete')
    @patch('xivo_dao.data_handler.user_line_extension.validator.validate_delete')
    def test_delete_with_error_from_dao(self, user_line_extension_dao_delete, user_line_extension_notifier_deleted, ule_validate):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        error = Exception("message")
        user_line_extension_dao_delete.side_effect = ElementDeletionError(error, '')

        ule_validate.return_value = (Mock(), Mock(), Mock())

        self.assertRaises(ElementDeletionError, user_line_extension_services.delete, ule)
        self.assertEquals(user_line_extension_notifier_deleted.call_count, 0)

    @patch('xivo_dao.data_handler.user.services.delete', Mock(return_value=None))
    @patch('xivo_dao.data_handler.line.services.delete', Mock(return_value=None))
    @patch('xivo_dao.data_handler.extension.services.delete', Mock(return_value=None))
    @patch('xivo_dao.data_handler.user_line_extension.validator.validate_delete')
    @patch('xivo_dao.data_handler.user_line_extension.notifier.deleted')
    @patch('xivo_dao.data_handler.user_line_extension.dao.delete')
    def test_delete_everything(self, user_line_extension_dao_delete, user_line_extension_notifier_deleted, ule_validate):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        ule_validate.return_value = (Mock(), Mock(), Mock())

        user_line_extension_services.delete_everything(ule)

        ule_validate.assert_called_once_with(ule)
        user_line_extension_dao_delete.assert_called_once_with(ule)
        user_line_extension_notifier_deleted.assert_called_once_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.notifier.deleted')
    @patch('xivo_dao.data_handler.user_line_extension.dao.delete')
    @patch('xivo_dao.data_handler.user_line_extension.validator.validate_delete')
    def test_delete_everything_with_error_from_dao(self, user_line_extension_dao_delete, user_line_extension_notifier_deleted, ule_validate):
        ule = UserLineExtension(user_id=5898,
                                line_id=52,
                                extension_id=52,
                                main_user=True,
                                main_line=False)

        error = Exception("message")
        user_line_extension_dao_delete.side_effect = ElementDeletionError(error, '')

        ule_validate.return_value = (Mock(), Mock(), Mock())

        self.assertRaises(ElementDeletionError, user_line_extension_services.delete_everything, ule)
