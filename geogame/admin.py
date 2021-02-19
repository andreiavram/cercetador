from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

# Register your models here.
from django.utils.safestring import mark_safe

from geogame.models import Zone, Tower, Team, Challenge, TeamTowerChallenge, TeamTowerOwnership


class ZoneAdmin(LeafletGeoAdmin):
    list_display = ['__str__', 'scoring_type', 'color', 'get_zone_control']

    def get_zone_control(self, instance):
        output = "<ul>"
        for option, title in Team.CATEGORY_CHOICES:
            zone_control_teams = instance.zone_control(option)
            output += "<li>{}: {}</li>\n".format(title, ",".join([t.__str__() for t in zone_control_teams]))

        output += "</ul>"

        return mark_safe(output)

    get_zone_control.allow_tags = True
    get_zone_control.short_description = "Controlled by"


class TowerAdmin(LeafletGeoAdmin):
    list_display = ['__str__', 'is_active', 'zone', 'category', 'get_tower_control']
    list_filter = ['zone', 'is_active', 'category']

    def get_tower_control(self, instance):
        output = "<ul>"
        for option, title in Team.CATEGORY_CHOICES:
            try:
                t = TeamTowerOwnership.objects.get(tower=instance, timestamp_end__isnull=True, team__category=option).team
            except TeamTowerOwnership.DoesNotExist:
                t = "NOT CONTROLLED"
            output += "<li>{}: {}</li>\n".format(title, t)
        output += "</ul>"

        return mark_safe(output)

    get_tower_control.allow_tags = True
    get_tower_control.short_description = "Controlled by"


class TeamAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'category', 'score', 'floating_score']
    list_filter = ['category']


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tower', 'difficulty']
    list_filter = ['tower']


class TeamTowerChallangeAdmin(admin.ModelAdmin):
    list_filter = ['checked_by', 'outcome']


admin.site.register(Zone, ZoneAdmin)
admin.site.register(Tower, TowerAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(TeamTowerChallenge, TeamTowerChallangeAdmin)