import json

from django.core import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels import Group
from channels.sessions import channel_session

from . import models
from .views.tournament_view import json_fields

def match_updates_group_name(tournament_slug):
    return "match-updates-%s" %(tournament_slug,)

@receiver(post_save, sender=models.TeamMatch,
        dispatch_uid="update_team_match")
def update_team_match(sender, instance, **kwargs):
    team_match_json = serializers.serialize('json', [instance],
            fields = json_fields['team_match'])
    tournament_slug = instance.division.tournament.slug
    group_name = match_updates_group_name(tournament_slug)
    message = {"text": team_match_json}
    Group(group_name).send(message)

@receiver(post_save, sender=models.Tournament,
        dispatch_uid="update_tournament")
def update_tournament(sender, instance, **kwargs):
    tournament_json = json.loads(serializers.serialize('json', [instance],
            fields=json_fields['tournament']))
    message = {"text": tournament_json}
    Group(instance.slug).send(message)

@channel_session
def match_updates_connect(message, tournament_slug):
    message.channel_session['tournament_slug'] = tournament_slug
    message.reply_channel.send({"accept": True})
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).add(message.reply_channel)

def process_update_message(message):
    raw_msgs = json.loads(message['text'])
    parsed_msgs = serializers.deserialize('json', message['text'])
    for raw_msg, parsed_msg in zip(raw_msgs, parsed_msgs):
        model_class = type(parsed_msg.object)
        model_instance = model_class.objects.get(pk=parsed_msg.object.pk)
        for model_attr in raw_msg['fields'].keys():
            model_attr_value = getattr(parsed_msg.object, model_attr)
            setattr(model_instance, model_attr, model_attr_value)
        model_instance.clean()
        model_instance.save()

@channel_session
def match_updates_message(message, tournament_slug):
    try:
        process_update_message(message)
    except Exception as e:
        err_msg = json.dumps({'error': str(e)})
        message.reply_channel.send({'text': err_msg})
        return
    message.channel_session['tournament_slug'] = tournament_slug
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).add(message.reply_channel)

@channel_session
def match_updates_disconnect(message):
    tournament_slug = message.channel_session['tournament_slug']
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).discard(message.reply_channel)
