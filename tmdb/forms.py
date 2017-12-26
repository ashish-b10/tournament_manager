from django import forms
import datetime

from . import models
from django.contrib.auth import models as auth_models

from collections import defaultdict

class TournamentEditForm(forms.ModelForm):
    import_field = forms.BooleanField(required=False, label="Import Schools?")

    class Meta:
        model = models.Tournament
        exclude = ['slug', 'imported']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.cleaned_data['import_field']:
            self.instance.import_school_registrations()

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
    tournament = forms.ModelChoiceField(
            queryset=models.Tournament.objects.all())

    def __init__(self, school_registration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tournament'].widget = forms.HiddenInput()
        self.fields['tournament_division'].widget = forms.HiddenInput()

        lst = ['lightweight', 'middleweight', 'heavyweight', 'alternate1',
                'alternate2', 'tournament_division']
        for key in self.fields:
            if key in lst:
                self.fields[key].required = False

        used_competitors = set()
        for i in models.TeamRegistration.objects.filter(
                team__school=school_registration.school,
                tournament_division__tournament=school_registration.tournament):
            used_competitors.update(i.get_competitors_ids())

        if 'instance' in kwargs:
            self.fields['team'].widget = forms.HiddenInput()
            used_competitors -= set(kwargs['instance'].get_competitors_ids())
        else:
            self.fields['team'].queryset = models.Team.objects.filter(
                school=school_registration.school,
                registrations=None).order_by('division', 'number')

        available_competitors = models.Competitor.objects.filter(
                registration=school_registration).exclude(
                        pk__in=used_competitors)

        self.fields['lightweight'].queryset = available_competitors
        self.fields['middleweight'].queryset = available_competitors
        self.fields['heavyweight'].queryset = available_competitors
        self.fields['alternate1'].queryset = available_competitors
        self.fields['alternate2'].queryset = available_competitors

    def clean(self):
        tournament = self.cleaned_data['tournament']
        division = self.cleaned_data['team'].division
        tournament_division = models.TournamentDivision.objects.get(
                tournament=tournament, division=division)
        self.cleaned_data['tournament_division'] = tournament_division

    class Meta:
        model = models.TeamRegistration
        exclude = ['seed', 'points']

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ring_assignment_time'].widget = forms.HiddenInput()

    def clean(self):
        if 'ring_number' in self.changed_data:
            self.cleaned_data['ring_assignment_time'] = datetime.datetime.now()
        return super(MatchForm, self).clean()

    class Meta:
        model = models.TeamMatch
        fields = ['ring_number', 'ring_assignment_time', 'winning_team', 'in_holding']

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

class TeamRegistrationPointsForm(forms.ModelForm):
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = models.TeamRegistration
        fields = ['points']

    def clean(self, *args, **kwargs):
        cleaned_data = super(TeamRegistrationPointsForm, self).clean(
                *args, **kwargs)
        confirm_delete_matches = cleaned_data['confirm_delete_matches']
        if confirm_delete_matches:
            return cleaned_data
        tournament_division = self.instance.tournament_division
        num_existing_matches = models.TeamMatch.objects.filter(
                division=tournament_division,
                winning_team__isnull=False).count()
        if not num_existing_matches:
            return cleaned_data
        self.fields['confirm_delete_matches'].widget = forms.CheckboxInput()
        raise forms.ValidationError("The %s division already has %d matches with results. Performing this operation will DELETE THESE MATCH RESULTS. Are you sure you want to do this?" %(str(tournament_division), num_existing_matches))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.tournament_division.assign_slots_to_team_registrations()
        self.instance.tournament_division.create_matches_from_slots()

class TeamRegistrationSeedingForm(forms.ModelForm):
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = models.TeamRegistration
        fields = ['seed']

    def clean(self, *args, **kwargs):
        cleaned_data = super(TeamRegistrationSeedingForm, self).clean(
                *args, **kwargs)
        confirm_delete_matches = cleaned_data['confirm_delete_matches']
        if confirm_delete_matches:
            return cleaned_data
        tournament_division = self.instance.tournament_division
        num_existing_matches = models.TeamMatch.objects.filter(
                division=tournament_division,
                winning_team__isnull=False).count()
        if not num_existing_matches:
            return cleaned_data
        self.fields['confirm_delete_matches'].widget = forms.CheckboxInput()
        raise forms.ValidationError("The %s division already has %d matches with results. Performing this operation will DELETE THESE MATCH RESULTS. Are you sure you want to do this?" %(str(tournament_division), num_existing_matches))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.tournament_division.create_matches_from_slots()

class TeamRegistrationBracketSeedingForm(forms.Form):
    seed = forms.IntegerField()
    team_registration = forms.ModelChoiceField(
            queryset=models.TeamRegistration.objects.all())
    existing_team = forms.ModelChoiceField(queryset=models.TeamRegistration.objects.all(), widget=forms.HiddenInput())
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())
    readonly_fields = ('seed',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seed'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super(
                TeamRegistrationBracketSeedingForm, self).clean()
        self.validate_schools()
        self.validate_weight_classes()
        self.validate_confirm_delete_matches()
        return cleaned_data

    def validate_weight_classes(self):
        """
        Raise a ValidationError if both teams do not have a competitor from a
        common weight class. (e.g. (L) vs (MH))
        """
        existing_team = self.cleaned_data['existing_team']
        new_team = self.cleaned_data['team_registration']
        if existing_team.lightweight and new_team.lightweight:
            return
        if existing_team.middleweight and new_team.middleweight:
            return
        if existing_team.heavyweight and new_team.heavyweight:
            return
        raise forms.ValidationError('Cannot match %s with %s (no competitors in the same weight class)' %(str(existing_team), str(new_team),))

    def validate_schools(self):
        """Raise a ValidationError if both teams come from the same school."""
        existing_team = self.cleaned_data['existing_team']
        new_team = self.cleaned_data['team_registration']
        if existing_team.team.school != new_team.team.school:
            return
        raise forms.ValidationError(
                "Cannot match two teams from the same school")

    def validate_confirm_delete_matches(self):
        """Raise a ValidationError if changing the bracket this way will delete
        matches with results already recorded."""
        confirm_delete_matches = self.cleaned_data['confirm_delete_matches']
        if confirm_delete_matches:
            return
        team_registration = self.cleaned_data['team_registration']
        division = team_registration.tournament_division
        num_existing_matches = models.TeamMatch.objects.filter(
                division=division, winning_team__isnull=False).count()
        if not num_existing_matches:
            return
        self.fields['confirm_delete_matches'].widget = forms.CheckboxInput()
        raise forms.ValidationError("The %s division already has %d matches with results. Performing this operation will DELETE THESE MATCH RESULTS. Are you sure you want to do this?" %(str(division.division), num_existing_matches))

    def save(self, *args, **kwargs):
        team_registration = self.cleaned_data['team_registration']
        team_registration.seed = self.cleaned_data['seed']
        team_registration.save()
        team_registration.tournament_division.create_matches_from_slots()

class TournamentDivisionBracketGenerateForm(forms.ModelForm):
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = models.TournamentDivision
        fields = []

    def clean(self):
        cleaned_data = super(
                TournamentDivisionBracketGenerateForm, self).clean()
        confirm_delete_matches = cleaned_data['confirm_delete_matches']
        if confirm_delete_matches:
            return cleaned_data
        num_existing_matches = models.TeamMatch.objects.filter(
                division=self.instance, winning_team__isnull=False).count()
        if not num_existing_matches:
            return cleaned_data
        self.fields['confirm_delete_matches'].widget = forms.CheckboxInput()
        raise forms.ValidationError("The %s division already has %d matches with results. Performing this operation will DELETE THESE MATCH RESULTS. Are you sure you want to do this?" %(str(self.instance.division), num_existing_matches))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.create_matches_from_slots()

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = auth_models.User
        fields = ('username', 'password')
