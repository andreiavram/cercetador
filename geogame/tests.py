from django.test import TestCase
from unittest.mock import MagicMock, patch

from geogame.models import Team, Tower, TeamZoneOwnership, TeamTowerOwnership, TeamTowerChallenge


class ZoneControlTest(TestCase):
    fixtures = ["tower_zones.json"]

    def setUp(self):
        self.t1 = Team.objects.create(name="explo1", category=Team.EXPLORATORI, code="EXPLO1", color="#003366")
        self.t2 = Team.objects.create(name="explo2", category=Team.EXPLORATORI, code="EXPLO2", color="#003366")

        self.tower1 = Tower.objects.get(name__icontains="Dendroparc")
        self.zone1 = self.tower1.zone

    @patch('geogame.models.Zone.get_score', MagicMock(return_value=1))
    def test_zone_control_from_empty(self):
        self.tower1.assign_to_team(self.t1)
        self.assertEqual(TeamZoneOwnership.objects.all().count(), 1)
        self.assertEqual(list(self.zone1.zone_control(self.t1.category)), [self.t1.pk])
        self.t1 = Team.objects.get(code="EXPLO1")
        self.t2 = Team.objects.get(code="EXPLO2")
        self.assertEqual(self.t1.score, 0)
        self.assertEqual(self.t2.score, 0)

        self.tower1.assign_to_team(self.t2)
        self.assertEqual(TeamZoneOwnership.objects.all().count(), 2)
        self.assertEqual(list(self.zone1.zone_control(self.t2.category)), [self.t2.pk])
        self.t1 = Team.objects.get(code="EXPLO1")
        self.t2 = Team.objects.get(code="EXPLO2")
        self.assertEqual(self.t1.score, 1)
        self.assertEqual(self.t2.score, 0)

        self.tower1.unassign()
        self.assertEqual(list(self.zone1.zone_control(self.t1.category)), [])
        self.assertEqual(TeamZoneOwnership.objects.all().count(), 2)
        self.t1 = Team.objects.get(code="EXPLO1")
        self.t2 = Team.objects.get(code="EXPLO2")
        self.assertEqual(self.t2.score, 1)
        self.assertEqual(self.t1.score, 1)

        self.tower1.assign_to_team(self.t1)
        self.tower1.unassign()
        self.assertEqual(TeamZoneOwnership.objects.all().count(), 3)
        self.t1 = Team.objects.get(code="EXPLO1")
        self.t2 = Team.objects.get(code="EXPLO2")
        self.assertEqual(self.t1.score, 2)
        self.assertEqual(self.t2.score, 1)

    def tearDown(self) -> None:
        TeamZoneOwnership.objects.all().delete()
        TeamTowerOwnership.objects.all().delete()
        TeamTowerChallenge.objects.all().delete()
