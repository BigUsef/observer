from django.test import SimpleTestCase

from utilities.restful.versioning import APIVersion


class TestVersionType(SimpleTestCase):
    def test_cast_version(self):
        version_number = '1.12.3.2'
        version = APIVersion.cast_version(version_number)
        self.assertTrue(isinstance(version, tuple))
        self.assertTrue(version[0], 1)
        self.assertTrue(version[1], 12)
        self.assertTrue(version[2], 3)
        self.assertTrue(version[3], 2)

    def test_valid_version_format(self):
        version_number = '1.2.3.4'
        version = APIVersion(version_number)
        self.assertEqual(version.header, version_number)
        self.assertEqual(version.release, 1)
        self.assertEqual(version.major, 2)
        self.assertEqual(version.minor, 3)
        self.assertEqual(version.patch, 4)

    def test_invalid_version_format(self):
        version_number = '1.2.3'
        with self.assertRaises(ValueError) as ex:
            APIVersion(version_number)

        self.assertIn('This version has wrong format,', str(ex.exception))

    def test_is_valid_version(self):
        version = APIVersion('1.9.12.8')

        self.assertTrue(version.is_valid('0.9.12.8'))
        self.assertTrue(version.is_valid('1.8.12.8'))
        self.assertTrue(version.is_valid('1.9.10.8'))
        self.assertTrue(version.is_valid('1.9.12.7'))

        self.assertFalse(version.is_valid('2.9.12.8'))
        self.assertFalse(version.is_valid('1.10.12.8'))
        self.assertFalse(version.is_valid('1.9.13.8'))
        self.assertFalse(version.is_valid('1.9.12.9'))

    def test_comparison_operators(self):
        self.assertTrue(APIVersion('1.2.4.0') == APIVersion('1.2.5.0'))
        self.assertTrue(APIVersion('1.2.4.0') == APIVersion('1.2.4.9'))
        self.assertTrue(APIVersion('1.2.4.0') == APIVersion('1.2.5.9'))
        self.assertFalse(APIVersion('1.2.4.0') == APIVersion('1.1.4.0'))
        self.assertFalse(APIVersion('1.2.4.0') == APIVersion('8.2.4.0'))
        self.assertFalse(APIVersion('1.2.4.0') == APIVersion('8.6.4.0'))

        self.assertTrue(APIVersion('1.2.4.0') != APIVersion('0.2.4.0'))
        self.assertTrue(APIVersion('1.2.4.0') != APIVersion('1.3.4.0'))
        self.assertTrue(APIVersion('1.2.4.0') != APIVersion('5.3.4.0'))
        self.assertFalse(APIVersion('1.2.4.0') != APIVersion('1.2.5.0'))
        self.assertFalse(APIVersion('1.2.4.0') != APIVersion('1.2.4.1'))
        self.assertFalse(APIVersion('1.2.4.0') != APIVersion('1.2.5.1'))

        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('0.1.3.0'))
        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('0.2.4.0'))
        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('1.1.4.2'))
        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('1.2.3.4'))
        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('0.3.5.3'))
        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('1.1.5.9'))
        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('0.16.5.12'))
        self.assertTrue(APIVersion('1.2.4.0') > APIVersion('1.1.23.1'))

        self.assertTrue(APIVersion('1.2.4.0') >= APIVersion('1.2.4.25'))

        self.assertTrue(APIVersion('1.2.4.0') < APIVersion('2.3.5.2'))
        self.assertTrue(APIVersion('1.2.4.0') < APIVersion('2.2.4.8'))
        self.assertTrue(APIVersion('1.2.4.0') < APIVersion('1.3.4.9'))
        self.assertTrue(APIVersion('1.2.4.0') < APIVersion('1.2.9.9'))
        self.assertTrue(APIVersion('1.2.4.0') < APIVersion('2.1.3.0'))
        self.assertTrue(APIVersion('1.2.4.0') < APIVersion('1.3.3.8'))
        self.assertTrue(APIVersion('1.2.34.0') < APIVersion('2.1.30.9'))
        self.assertTrue(APIVersion('1.2.44.0') < APIVersion('1.3.35.9'))

        self.assertTrue(APIVersion('1.2.4.0') <= APIVersion('1.2.4.10'))

