from django import forms
import datetime

from . import models
from django.contrib.auth import models as auth_models

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

class TeamRegistrationDeleteForm(forms.ModelForm):
    class Meta:
        model = models.TeamRegistration
        fields = []

class TeamRegistrationForm(forms.ModelForm):
    def __init__(self, school, school_registration, used_competitors, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lst = ['lightweight', 'middleweight', 'heavyweight', 'alternate1', 'alternate2']

        for key in self.fields:
            if key in lst:
                self.fields[key].required = False

        if len(kwargs) != 0:
            self.fields['team'].queryset = models.Team.objects.filter(school=school, registrations__in=[None, kwargs['instance'].tournament_division])
        else:
            self.fields['team'].queryset = models.Team.objects.filter(school=school, registrations=None)
        self.fields['lightweight'].queryset = models.Competitor.objects.filter(registration=school_registration).exclude(pk__in=used_competitors)
        self.fields['middleweight'].queryset = models.Competitor.objects.filter(registration=school_registration).exclude(pk__in=used_competitors)
        self.fields['heavyweight'].queryset = models.Competitor.objects.filter(registration=school_registration).exclude(pk__in=used_competitors)
        self.fields['alternate1'].queryset = models.Competitor.objects.filter(registration=school_registration).exclude(pk__in=used_competitors)
        self.fields['alternate2'].queryset = models.Competitor.objects.filter(registration=school_registration).exclude(pk__in=used_competitors)

    class Meta:
        model = models.TeamRegistration
        exclude = ['seed', 'points']

class SchoolRegistrationImportForm(forms.Form):
    school_registrations = forms.CharField(required=True,
            widget=forms.HiddenInput())
    reimport = forms.BooleanField(required=False, widget=forms.HiddenInput())

class SchoolCompetitorForm(forms.ModelForm):
    class Meta:
        model = models.Competitor
        fields = ['name', 'sex', 'belt_rank', 'weight', 'registration']
        widgets = {
            'registration': forms.HiddenInput(),
        }

class SchoolCompetitorDeleteForm(forms.ModelForm):
    class Meta:
        model = models.Competitor
        fields = []

class MatchForm(forms.ModelForm):
    def clean(self):
        if 'ring_number' in self.changed_data:
            self.cleaned_data['ring_assignment_time'] = datetime.datetime.now()
        return super(MatchForm, self).clean()

    class Meta:
        model = models.TeamMatch
        fields = ['ring_number', 'ring_assignment_time', 'winning_team', 'in_holding']

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

class TeamRegistrationSeedingForm(forms.Form):
    seed = forms.IntegerField()
    team_registration = forms.ModelChoiceField(
            queryset=models.TeamRegistration.objects.all())
    readonly_fields = ('seed',)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = auth_models.User
        fields = ('username', 'password')
