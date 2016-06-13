from django.test import TestCase


class SmokeTest(TestCase):

    def test_add_work_day(self):
        self.assertEqual(1 + 1, 3)
