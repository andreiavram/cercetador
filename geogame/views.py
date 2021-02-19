from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from rest_framework import viewsets
from rest_framework import permissions

from geogame.models import Zone, Tower, Team, Challenge
from geogame.serializers import ZoneSerializer, TowerSerializer, TeamSerializer, ChallengeSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.exclude(tower__is_active=False)
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TowerViewSet(viewsets.ModelViewSet):
    queryset = Tower.objects.exclude(is_active=False)
    serializer_class = TowerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MapView(TemplateView):
    template_name = "geogame/map.html"


class RFIDTowerView(DetailView):
    template_name = "geogame/tower_rfid.html"
    model = Tower

    def get_object(self, queryset=None):
        return Tower.objects.get(rfid_code=self.kwargs.get("rfid_code"))


class TowerChallengeView(TemplateView):
    template_name = "geogame/tower_challenge.html"

