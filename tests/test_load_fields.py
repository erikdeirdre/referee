from os.path import join, dirname
import unittest
from referee import load_fields


class TestLoadFields(unittest.TestCase):
    def test_valid_file(self):
        expected_fields = {
            'Field1': 'Field One @ High School', 'Field2': 'Field Two @ HS'
        }
        fields, rc = load_fields(join(dirname(__file__),'files' ,'test_fields.csv'))
        self.assertEqual(rc, 0)
        self.assertEqual(fields, expected_fields)

    def test_invalid_file(self):
        with self.assertLogs(level='INFO') as cm:
            fields, rc = load_fields('file_does_not_exist.csv')
        self.assertEqual(
            cm.output, ["ERROR:root:No such file or directory: file_does_not_exist.csv"]
        )
        self.assertEqual(rc, 66)
        self.assertEqual(fields, {})