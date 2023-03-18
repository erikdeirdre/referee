import unittest
from referee import get_age_gender

class TestGetAgeGender(unittest.TestCase):
# expected format "Grade 3/4 Boys"
    def test_get_male(self):
        gender, age_group = get_age_gender("Grade 3/4 Boys")
        self.assertEqual(gender, 'M')
        self.assertEqual(age_group, '3/4')

    def test_get_female(self):
        gender, age_group = get_age_gender("Grade 3/4 Girls")
        self.assertEqual(gender, 'F')
        self.assertEqual(age_group, '3/4')
