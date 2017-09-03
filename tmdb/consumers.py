import json

from django.core import serializers
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user_from_http, channel_session_user

from . import models
from .views.tournament_view import json_fields

def match_updates_group_name(tournament_slug):
    return "match-updates-%s" %(tournament_slug,)

def create_message(message_type, message_content, dump_message_content=True):
    if dump_message_content:
        message_content = json.dumps(message_content)
    return {'text': json.dumps({message_type: message_content})}

@receiver(post_save, sender=models.TeamMatch,
        dispatch_uid="update_team_match")
def update_team_match(sender, instance, **kwargs):
    team_match_json = serializers.serialize('json', [instance],
            fields = json_fields['team_match'])
    tournament_slug = instance.division.tournament.slug
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).send(create_message('update', team_match_json,
            dump_message_content=False), immediately=True)

@receiver(post_delete, sender=models.TeamMatch,
        dispatch_uid="delete_team_match")
def delete_team_match(sender, instance, **kwargs):
    team_match_json = serializers.serialize('json', [instance], fields = [])
    tournament_slug = instance.division.tournament.slug
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).send(create_message('delete', team_match_json,
            dump_message_content=False), immediately=True)

@receiver(post_save, sender=models.Tournament,
        dispatch_uid="update_tournament")
def update_tournament(sender, instance, **kwargs):
    tournament_json = json.loads(serializers.serialize('json', [instance],
            fields=json_fields['tournament']))
    message = {"text": tournament_json}
    Group(instance.slug).send(message)

@channel_session_user_from_http
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

@channel_session_user
def match_updates_message(message, tournament_slug):
    if not message.user.has_perm('tmdb.change_teammatch'):
        err_msg = str(message.user)
        err_msg += " does not have permission to change this value"
        message.reply_channel.send(create_message('error', err_msg))
        return
    try:
        process_update_message(message)
    except Exception as e:
        message.reply_channel.send(create_message('error', str(e)))
        return
    message.channel_session['tournament_slug'] = tournament_slug
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).add(message.reply_channel)

@channel_session
def match_updates_disconnect(message):
    tournament_slug = message.channel_session['tournament_slug']
    group_name = match_updates_group_name(tournament_slug)
    Group(group_name).discard(message.reply_channel)
