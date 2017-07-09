import json

from django.core import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels import Group
from channels.sessions import channel_session

from . import models

def match_updates_group_name(tournament_slug):
    return "match-updates-%s" %(tournament_slug,)

def model_to_json(query_set, fields):
    obj_json = serializers.serialize('json', query_set, fields=fields)
    return json.loads(obj_json)

def initial_tournament_data(tournament_slug):
    msg = []
    tournament = models.Tournament.objects.get(slug=tournament_slug)
    msg.extend(model_to_json(
            [tournament],
            ('id', 'location', 'date',)))
    msg.extend(model_to_json(
            models.Division.objects.all(),
            ('id', 'sex', 'skill_level',)))
    msg.extend(model_to_json(
            models.School.objects.all(),
            ('id', 'name',)))
    msg.extend(model_to_json(
            models.Team.objects.all(),
            ('id', 'division', 'school', 'number',)))
    msg.extend(model_to_json(
            models.TournamentDivision.objects.filter(tournament=tournament),
            ('id', 'division', 'tournament',)))
    msg.extend(model_to_json(
            models.SchoolRegistration.objects.filter(tournament=tournament),
            ('id', 'school', 'tournament',)))
    msg.extend(model_to_json(
            models.Competitor.objects.filter(
                    registration__tournament=tournament),
            ('id', 'registration', 'belt_rank', 'name', 'sex',)))
    msg.extend(model_to_json(
            models.TeamRegistration.objects.filter(
                    tournament_division__tournament=tournament),
            ('id', 'lightweight', 'middleweight', 'heavyweight', 'alternate1',
                    'alternate2', 'team', 'tournament_division', 'points',
                    'seed',)))
    msg.extend(model_to_json(
            models.TeamMatch.objects.filter(division__tournament=tournament),
            ('id', 'blue_team', 'red_team', 'winning_team', 'division',
                    'in_holding', 'number', 'ring_assignment_time',
                    'ring_number', 'round_num', 'round_slot',)))

    return msg

@receiver(post_save, sender=models.TeamMatch,
        dispatch_uid="update_team_matches")
def update_team_matches(sender, instance, **kwargs):
    tournament_slug = instance.division.tournament.slug
    group_name = match_updates_group_name(tournament_slug)
    message = {"text": "updated match %d" %(instance.pk,)}
    Group(group_name).send(message)

@channel_session
def match_updates_connect(message, tournament_slug):
    message.channel_session['tournament_slug'] = tournament_slug
    message.reply_channel.send({"accept": True})
    message.reply_channel.send(
            {"text": json.dumps(initial_tournament_data(tournament_slug))})
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).add(message.reply_channel)

@channel_session
def match_updates_message(message, tournament_slug):
    message.channel_session['tournament_slug'] = tournament_slug
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).add(message.reply_channel)

@channel_session
def match_updates_disconnect(message):
    tournament_slug = message.channel_session['tournament_slug']
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).discard(message.reply_channel)
