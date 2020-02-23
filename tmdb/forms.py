from django import forms
import datetime

from tmdb import models
from django.contrib.auth import models as auth_models

class SeasonAddChangeForm(forms.ModelForm):
    class Meta:
        model = models.Season
        exclude = ['slug', 'schools',]

    def __init__(self, *args, **kwargs):
        super(SeasonAddChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        start_date=self.cleaned_data['start_date']
        if 'end_date' not in self.cleaned_data or not self.cleaned_data['end_date']:
            self.cleaned_data['end_date'] = start_date.replace(
                    year=start_date.year+1)

class SeasonDeleteForm(forms.ModelForm):
    class Meta:
        model = models.Season
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
        model = models.SparringTeamMatch
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

class SparringTeamRegistrationPointsForm(forms.ModelForm):
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = models.SparringTeamRegistration
        fields = ['points']

    def clean(self, *args, **kwargs):
        cleaned_data = super(SparringTeamRegistrationPointsForm, self).clean(
                *args, **kwargs)
        confirm_delete_matches = cleaned_data['confirm_delete_matches']
        if confirm_delete_matches:
            return cleaned_data
        tournament_division = self.instance.tournament_division
        num_existing_matches = models.SparringTeamMatch.objects.filter(
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

class SparringTeamRegistrationSeedingForm(forms.ModelForm):
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = models.SparringTeamRegistration
        fields = ['seed']

    def clean_seed(self):
        if self.cleaned_data['seed'] is None:
            return
        existing_seeds = models.SparringTeamRegistration.objects.filter(
                tournament_division=self.instance.tournament_division,
                seed=self.cleaned_data['seed'])
        if existing_seeds:
            raise forms.ValidationError("A team already has seed #%d: %s" %(
                    self.cleaned_data['seed'], existing_seeds.first().team))

    def clean(self, *args, **kwargs):
        confirm_delete_matches = self.cleaned_data['confirm_delete_matches']
        if confirm_delete_matches:
            return self.cleaned_data
        tournament_division = self.instance.tournament_division
        num_existing_matches = models.SparringTeamMatch.objects.filter(
                division=tournament_division,
                winning_team__isnull=False).count()
        if not num_existing_matches:
            return self.cleaned_data
        self.fields['confirm_delete_matches'].widget = forms.CheckboxInput()
        raise forms.ValidationError("The %s division already has %d matches with results. Performing this operation will DELETE THESE MATCH RESULTS. Are you sure you want to do this?" %(str(tournament_division), num_existing_matches))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.tournament_division.create_matches_from_slots()

class SparringTeamRegistrationBracketSeedingForm(forms.Form):
    seed = forms.IntegerField()
    team_registration = forms.ModelChoiceField(
            queryset=models.SparringTeamRegistration.objects.all())
    existing_team = forms.ModelChoiceField(
            queryset=models.SparringTeamRegistration.objects.all(),
            widget=forms.HiddenInput())
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())
    readonly_fields = ('seed',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seed'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super(
                SparringTeamRegistrationBracketSeedingForm, self).clean()
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
        num_existing_matches = models.SparringTeamMatch.objects.filter(
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

class TournamentSparringDivisionBracketGenerateForm(forms.ModelForm):
    confirm_delete_matches = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = models.TournamentSparringDivision
        fields = []

    def clean(self):
        cleaned_data = super(
                TournamentSparringDivisionBracketGenerateForm, self).clean()
        confirm_delete_matches = cleaned_data['confirm_delete_matches']
        if confirm_delete_matches:
            return cleaned_data
        num_existing_matches = models.SparringTeamMatch.objects.filter(
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
