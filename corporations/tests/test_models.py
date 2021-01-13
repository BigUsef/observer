from django.test import TestCase
from model_bakery import baker


class TestFacility(TestCase):
    def setUp(self) -> None:
        branches = baker.prepare('corporations.Branch', is_main=False, _quantity=5)
        self.main_branch = baker.prepare('corporations.Branch', is_main=True)
        branches.append(self.main_branch)

        self.facility = baker.make('corporations.Facility', branches=branches)

    def test_get_main_branch(self):
        self.assertEqual(self.facility.main_branch.id, self.main_branch.id)
        self.assertEqual(self.facility.main_branch.name, self.main_branch.name)

    def tearDown(self) -> None:
        self.facility.delete()
