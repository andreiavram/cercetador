from django.db.models import Count, Q
from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from geogame.models import Zone, Tower, Team, Challenge, TeamTowerChallenge
from geogame.serializers import ZoneSerializer, TowerSerializer, TeamSerializer, ChallengeSerializer, \
    TeamTowerChallengeSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Zone.objects.annotate(num_towers=Count('tower', Q(tower__is_active=True))).filter(num_towers__gte=1)

    def get_serializer_context(self):
        context = super(ZoneViewSet, self).get_serializer_context()
        context['category'] = self.request.query_params.get('category', 0)
        return context


class TowerViewSet(viewsets.ModelViewSet):
    queryset = Tower.objects.exclude(is_active=False).exclude(category=Tower.CATEGORY_RFID)
    serializer_class = TowerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super(TowerViewSet, self).get_queryset()
        if self.request.query_params.get("lat") and self.request.query_params.get("lng"):
            lat = float(self.request.query_params.get("lat"))
            lng = float(self.request.query_params.get("lng"))
            point = Point(lng, lat)
            radius = min(float(self.request.query_params.get("accuracy", 100.)), 50.)

            return queryset.filter(location__distance_lt=(point, Distance(m=radius)))
        return queryset


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        category = int(self.request.query_params.get("category", 0))
        if category:
            return Team.objects.filter(category=category)
        return self.queryset

    def get_serializer_context(self):
        context = super(TeamViewSet, self).get_serializer_context()
        context['category'] = self.request.query_params.get('category', 0)
        return context


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TeamTowerChallengeViewSet(viewsets.ModelViewSet):
    queryset = TeamTowerChallenge.objects.all()
    serializer_class = TeamTowerChallengeSerializer
    permission_classes = [permissions.AllowAny]


class MapView(TemplateView):
    template_name = "geogame/map.html"


class ScoreMapView(TemplateView):
    template_name = "geogame/map_score.html"

    def get_context_data(self, **kwargs):
        context = super(ScoreMapView, self).get_context_data(**kwargs)

        context['team_category'] = self.kwargs.get("category", Team.EXPLORATORI)
        return context


class RFIDTowerView(DetailView):
    template_name = "geogame/tower_rfid.html"
    model = Tower

    def get_object(self, queryset=None):
        return Tower.objects.get(rfid_code=self.kwargs.get("rfid_code"))


class TowerChallengeView(TemplateView):
    template_name = "geogame/tower_challenge.html"


class TowerDetailView(DetailView):
    model = Tower

    def dispatch(self, request, *args, **kwargs):
        self.lat = float(request.GET.get("lat", 0.))
        self.lng = float(request.GET.get("lng", 0.))
        if not request.user.is_authenticated:
            if not self.lng or not self.lat:
                return HttpResponseBadRequest("Nu esti langa obiectiv!")

        self.team_code = request.GET.get("team_code")
        self.team = None
        if self.team_code:
            try:
                self.team = Team.objects.get(code=self.team_code)
            except Team.DoesNotExist:
                raise Http404("Codul tău de echipă nu e corect!")
        return super(TowerDetailView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(TowerDetailView, self).get_object(queryset)
        if not self.request.user.is_authenticated:
            point = Point(self.lng, self.lat)
            radius = 50
            try:
                Tower.objects.get(pk=obj.id, location__distance_lt=(point, Distance(m=radius)))
            except Tower.DoesNotExist:
                raise Http404("Nu ești lângă obiectiv!")

        return obj

    def get_context_data(self, **kwargs):
        context = super(TowerDetailView, self).get_context_data(**kwargs)
        context['lat'] = self.lat
        context['lng'] = self.lng
        context['team'] = self.team
        if self.team:
            context['tower_owner'] = self.object.tower_control(category=self.team.category)
            context['challenge'] = self.object.get_next_challenge(self.team)
            context['team_has_pending'] = self.object.team_pending(self.team)
            context['team_in_cooloff'] = self.object.team_in_cooloff(self.team)
        return context



