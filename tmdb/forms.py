from django import forms
import datetime

from . import models

from collections import defaultdict

class TournamentEditForm(forms.ModelForm):
    class Meta:
        model = models.Tournament
        exclude = ['slug', 'imported']

class TournamentDeleteForm(forms.ModelForm):
    class Meta:
        model = models.Tournament
        fields = []

class TournamentImportForm(forms.ModelForm):
    class Meta:
        model = models.Tournament
        fields = []

class SchoolRegistrationImportForm(forms.Form):
    school_registrations = forms.CharField(required=True,
            widget=forms.HiddenInput())
    reimport = forms.BooleanField(required=False, widget=forms.HiddenInput())

class MatchForm(forms.ModelForm):
    def clean(self):
        if 'ring_number' in self.changed_data:
            self.cleaned_data['ring_assignment_time'] = datetime.datetime.now()
        return super(MatchForm, self).clean()

    class Meta:
        model = models.TeamMatch
        fields = ['ring_number', 'ring_assignment_time', 'winning_team']

class TeamPointsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['points'].label = str(self.instance)

    class Meta:
        model = models.TeamRegistration
        fields = ['id', 'points']

class SeedingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seed'].label = str(self.instance)

    class Meta:
        model = models.TeamRegistration
        fields = ['id', 'seed']

    @staticmethod
    def modified_teams(seed_forms):
        return [form.save(commit=False) for form in seed_forms]

    @staticmethod
    def all_seeds_valid(seed_forms):
        errors = []
        modified_teams = SeedingForm.modified_teams(seed_forms)
        for team in modified_teams:
            if team.seed is None: continue
            if team.seed >= 1: continue
            errors.append(forms.ValidationError("Team " + str(team) + " has"
                    + " seed < 1 (%d)" %team.seed))
        tournament_divisions = {form_team.tournament_division
                for form_team in modified_teams}
        if len(tournament_divisions) > 1:
            errors.append(forms.ValidationError("Cannot handle teams from"
                    + " multiple TournamentDivisions (teams supplied have %s)"
                    %(tournament_divisions)))
            raise forms.ValidationError(errors)
        tournament_division = tournament_divisions.pop()

        teams = {t.id:t for t in models.TeamRegistration.objects.filter(
                tournament_division=tournament_division)}
        for team in modified_teams:
            teams[team.id] = team
        filled_seeds = defaultdict(list)
        for team in teams.values():
            if team.seed is None: continue
            filled_seeds[team.seed].append(team)
        duplicated_seeds = {seed:teams for seed,teams in filled_seeds.items()
                if len(teams) > 1}
        if duplicated_seeds:
            errors.append(forms.ValidationError("The following seeds have"
                    + " multiple teams assigned: " + str(duplicated_seeds)))
        if errors:
            raise forms.ValidationError(errors)
        return tournament_division

class ConfigurationSetting(forms.ModelForm):
    class Meta:
        model = models.ConfigurationSetting
        exclude = []
        widgets = {
            'key': forms.HiddenInput(),
            'value': forms.Textarea()
        }
        labels = {
            'value': ''
        }
