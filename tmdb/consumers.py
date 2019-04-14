import json

from django.core import serializers
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from . import models
from .views.tournament_view import json_fields

def match_updates_group_name(tournament_slug):
    return "match-updates-%s" %(tournament_slug,)

def create_message(message_type, message_content, dump_message_content=True):
    if dump_message_content:
        message_content = json.dumps(message_content)
    return json.dumps({
            'message_type': message_type,
            'message_content': message_content})

@receiver([post_save, post_delete], sender=models.SparringTeamMatch,
        dispatch_uid="update_team_match")
def update_team_match(sender, instance, **kwargs):
    team_match_json = json.loads(serializers.serialize('json', [instance],
            fields = json_fields['team_match']))
    tournament_slug = instance.division.tournament.slug
    group_name = match_updates_group_name(tournament_slug)
    async_to_sync(get_channel_layer().group_send)(group_name, {
        'type': 'update_sparring_team_match',
        'message': create_message('update', team_match_json,
            dump_message_content=False)
    })

class SparringTeamMatchConsumer(WebsocketConsumer):
    def connect(self):
        self.tournament_slug = self.scope['url_route']['kwargs']['tournament_slug']
        self.sparring_team_match_group = match_updates_group_name(
                self.tournament_slug)
        async_to_sync(self.channel_layer.group_add)(
                self.sparring_team_match_group, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
                self.sparring_team_match_group, self.channel_name)

    def receive(self, text_data):
        if not self.scope['user'].has_perm('tmdb.change_teammatch'):
            err_msg = str(self.scope['user'])
            err_msg += " does not have permission to change this value"
            self.send(create_message('error', err_msg))
            return
        try:
            SparringTeamMatchConsumer.process_update_message(text_data)
        except Exception as e:
            self.send(create_message('error', str(e)))
            return

    def update_sparring_team_match(self, event):
        message = event['message']
        self.send(text_data=message)

    @staticmethod
    def process_update_message(text_data):
        raw_msgs = json.loads(text_data)
        parsed_msgs = serializers.deserialize('json', text_data)
        for raw_msg, parsed_msg in zip(raw_msgs, parsed_msgs):
            model_class = type(parsed_msg.object)
            model_instance = model_class.objects.get(pk=parsed_msg.object.pk)
            for model_attr in raw_msg['fields'].keys():
                model_attr_value = getattr(parsed_msg.object, model_attr)
                setattr(model_instance, model_attr, model_attr_value)
            model_instance.clean()
            model_instance.save()
