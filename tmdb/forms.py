from django import forms

from .models import TeamMatch

class MatchForm(forms.ModelForm):
    class Meta:
        model = TeamMatch
        fields = ['ring_number', 'winning_team']
