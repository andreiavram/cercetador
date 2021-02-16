from django.contrib.gis.db import models
from django.conf import settings
from django.db.models import Count, Max
from datetime import datetime, timezone


class Zone(models.Model):
    SCORE_LOG = 1
    SCORE_EXP = 2
    SCORE_LIN = 3

    ZONE_SCORING_CHOICES = [
        (SCORE_LOG, "Multe puncte la început, tot mai puține apoi"),
        (SCORE_EXP, "Putine puncte la început, tot mai multe apoi"),
        (SCORE_LIN, "Puncte proportional cu posesia")
    ]

    name = models.CharField(max_length=255)
    color = models.CharField(max_length=6)
    scoring_type = models.PositiveSmallIntegerField(choices=ZONE_SCORING_CHOICES)
    shape = models.PolygonField(null=True, blank=True)

    def __str__(self):
        return self.name

    def zone_control(self, category):
        towers_count = self.tower_set.count()
        if towers_count == 1:
            try:
                return [TeamTowerOwnership.objects.get(timestamp_end__isnull=True, team__category=category).team, ]
            except TeamTowerOwnership.DoesNotExist as e:
                return None
            except TeamTowerOwnership.MultipleObjectsReturned:
                # TODO: log this here, this should never happen
                pass
        elif towers_count > 1:
            # this means that this zone has more than one tower
            # the algorithm here is that all the teams that have the biggest number of towers under their control
            # control the zone

            team_stats = TeamTowerOwnership.objects.filter(timestamp_end__isnull=True, team__category=category)\
                .values('team').annotate(tower_count=Count('tower'))

            max_towers = max((stat['tower_count'] for stat in team_stats))
            team_ids = (stat['team'] for stat in team_stats if stat['tower_count'] == max_towers)

            # force list here to ensure compatibility with one team scenarios
            teams = list(Team.objects.filter(pk__in=team_ids))
            return teams


class Tower(models.Model):
    CATEGORY_NORMAL = 1
    CATEGORY_RFID = 2
    CATEGORY_CHOICES = [
        (CATEGORY_NORMAL, "Normal"),
        (CATEGORY_RFID, "RFID")
    ]

    name = models.CharField(max_length=255)
    location = models.PointField()
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    category = models.PositiveSmallIntegerField()
    is_active = models.BooleanField()
    # TODO: add tower image

    def __str__(self):
        return self.name

    def assign_to_team(self, team, challenge):
        handover_time = datetime.now(timezone.utc)
        try:
            ownership = TeamTowerOwnership.objects.get(tower=self, timestamp_end__isnull=True, team__category=team.category)
            ownership.timestamp_end = handover_time
            ownership.save()
        except TeamTowerOwnership.DoesNotExist:
            pass

        return TeamTowerOwnership.objects.create(tower=self, team=team, timestamp_start=handover_time)

    def get_next_challenge(self, team):
        # TODO: cooloff period? do we need this
        #   get max current successful level for this team at this tower
        max_difficulty = TeamTowerChallenge.objects.filter(team=team, tower=self, outcome=TeamTowerChallenge.CONFIRMED)\
            .aggregate(max_difficulty=Max('challenge_difficulty'))['max_difficulty']
        #   try and get next available challenge for tower, at this difficulty or higher
        used_challenges_ids = TeamTowerChallenge.objects.filter(tower=self, team=team).values_list('team', flat=True)
        challenge = Challenge.objects.exclude(pk__in=used_challenges_ids)\
            .filter(tower=self, difficulty__gte=max_difficulty).order_by("difficulty").first()
        if challenge:
            return challenge

        challenge = Challenge.objects.exclude(pk__in=used_challenges_ids)\
            .filter(difficulty__gte=max_difficulty).order_by("difficulty").first()
        if challenge:
            return challenge

        # TODO: out of challenges, what now?
        # Returning toughest challenge for now
        return Challenge.objects.filter(tower__isnull=True).order_by("-difficulty").first()


class Team(models.Model):
    EXPLORATORI = 1
    TEMERARI = 2
    SENIORI = 3
    CATEGORY_CHOICES = [
        (EXPLORATORI, "eXplo"),
        (TEMERARI, "Temerari"),
        (SENIORI, "Seniori")
    ]

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=8, unique=True)
    category = models.PositiveSmallIntegerField(choices=CATEGORY_CHOICES)

    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Challenge(models.Model):
    text = models.TextField(null=False, blank=False)
    tower = models.ForeignKey(Tower, null=True, blank=True, on_delete=models.CASCADE)
    difficulty = models.PositiveSmallIntegerField(default=1)


class TeamTowerChallenge(models.Model):
    CONFIRMED = 1
    REJECTED = 2

    OUTCOME_CHOICES = [
        (CONFIRMED, "Confirmat"),
        (REJECTED, "Respins")
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    timestamp_submitted = models.DateTimeField(auto_now_add=True)
    timestamp_verified = models.DateTimeField(null=True, blank=True)
    outcome = models.PositiveSmallIntegerField(choices=OUTCOME_CHOICES, null=True, blank=True)
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    response_text = models.TextField(null=True, blank=True)
    # TODO: add response image

    def __init__(self, *args, **kwargs):
        super(TeamTowerChallenge, self).__init__(*args, **kwargs)
        self.__original_outcome = self.outcome

    def save(self, *args, **kwargs):
        #   if the team completed the challenge
        if self.__original_outcome != self.outcome:
            if self.outcome == TeamTowerChallenge.CONFIRMED:
                self.tower.assign_to_team(self.team, self.challenge)
        super(TeamTowerChallenge, self).save(*args, **kwargs)


class TeamTowerOwnership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    timestamp_start = models.DateTimeField(auto_now_add=True)
    timestamp_end = models.DateTimeField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(TeamTowerOwnership, self).__init__(*args, **kwargs)
        self.__timestamp_end = self.timestamp_end

    def get_ownership_time(self):
        if self.timestamp_end:
            return (self.timestamp_end - self.timestamp_start).seconds
        return (datetime.now(timezone.utc) - self.timestamp_start).seconds

    def __str__(self):
        data = (self.team, self.tower, self.get_ownership_time())
        if self.timestamp_end:
            return "{} owned {} for {}s".format(*data)
        return "{} owns {} for {}s".format(*data)

    def save(self, *args, **kwargs):
        super(TeamTowerOwnership, self).save(*args, **kwargs)
        if self.__timestamp_end != self.timestamp_end and self.timestamp_end is not None:
            #   tower ownership has finished, give team its points
            self.team.score += self.tower.zone.final_score(self)