"""cercetador URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from geogame.views import ZoneViewSet, TowerViewSet, TeamViewSet, ChallengeViewSet, MapView, RFIDTowerView, \
    TowerChallengeView
from django.conf import settings
from django.conf.urls.static import static


router = routers.DefaultRouter()
router.register(r'zones', ZoneViewSet)
router.register(r'towers', TowerViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'challenges', ChallengeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MapView.as_view()),
    path('tower/rfid/<str:rfid_code>/', RFIDTowerView.as_view(), name='tower-rfid'),
    path('tower/challenge/', TowerChallengeView.as_view(), name='tower-challenge'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

