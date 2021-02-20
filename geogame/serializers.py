from rest_framework import serializers

from geogame.models import Zone, Tower, Team, Challenge


class ZoneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Zone
        fields = ["name", "color", "scoring_type", "shape", "team_color"]

    team_color = serializers.SerializerMethodField()

    def get_team_color(self, zone):
        category = int(self.context.get("category", 0))
        if category:
            control_team_ids = zone.zone_control(category=category)
            teams = Team.objects.filter(pk__in=control_team_ids)
            if teams.count() > 1:
                return "#FFFFFF"
            elif teams.count() == 1:
                return teams.first().color
        return "#000000"


class TowerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tower
        fields = ["name", "location", "zone", "category", "is_active", "ownership", "id"]

    ownership = serializers.SerializerMethodField()

    def get_ownership(self, obj):
        #   TODO: fix this
        return TeamSerializer(obj.tower_control(1)).data


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "code", "category", "current_score", "color"]


class ChallengeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Challenge
        fields = ["text", "tower", "difficulty"]