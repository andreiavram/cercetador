from rest_framework import serializers

from geogame.models import Zone, Tower, Team, Challenge


class ZoneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Zone
        fields = ["name", "color", "scoring_type", "shape"]

    def get_zone_ownership(self):
        pass


class TowerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tower
        fields = ["name", "location", "zone", "category", "is_active", "ownership"]

    ownership = serializers.SerializerMethodField()

    def get_ownership(self, obj):
        #   TODO: fix this
        return TeamSerializer(obj.tower_control(1)).data


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "code", "category"]


class ChallengeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Challenge
        fields = ["text", "tower", "difficulty"]