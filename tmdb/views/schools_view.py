from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect

from tmdb import models

def schools(request):
    schools = models.School.objects.all()
    context = {
            'schools': schools
    }
    return render(request, 'tmdb/schools.html', context)

def school(request, school_slug):
    school = get_object_or_404(models.School, slug=school_slug)
    registrations = models.SchoolSeasonRegistration.objects.filter(
            school=school).order_by('season__start_date')
    context = {
            'school': school,
            'school_season_registrations': registrations,
    }
    return render(request, 'tmdb/school.html', context)

class SchoolSeasonRegistrationAddChangeForm(forms.ModelForm):
    class Meta:
        model = models.SchoolSeasonRegistration
        exclude = ['school', 'season']

    def __init__(self, *args, **kwargs):
        super(SchoolSeasonRegistrationAddChangeForm, self).__init__(
                *args, **kwargs)
        division_widget = forms.Select(
                choices=((1,"Div #1"), (2,"Div #2"),(3, "Div #3")))
        if self.instance:
            division_widget.initial = self.instance.division
        else:
            division_widget.initial = 3
        self.fields['division'].widget = division_widget

@permission_required("tmdb.change_schoolseasonregistration")
def school_season_change(request, school_slug, season_slug):
    instance = get_object_or_404(models.SchoolSeasonRegistration,
            school__slug=school_slug, season__slug=season_slug)
    template_name = 'tmdb/school_season_registration_change.html'
    context = {}
    if request.method == 'POST':
        change_form = SchoolSeasonRegistrationAddChangeForm(request.POST,
                instance=instance)
        if change_form.is_valid():
            change_form.save()
            return HttpResponseRedirect(reverse('tmdb:school',
                    args=(school_slug,)))
    else:
        change_form = SchoolSeasonRegistrationAddChangeForm(
                instance=instance)
    context['change_form'] = change_form
    return render(request, template_name, context)

class SchoolForm(forms.ModelForm):
    class Meta:
        model = models.School
        fields = ['name']

@permission_required("tmdb.change_school")
def school_add(request):
    template_name = 'tmdb/school_add_change.html'
    context = {}
    if request.method == 'POST':
        add_form = SchoolForm(request.POST)
        if add_form.is_valid():
            new_school = add_form.save()
            return HttpResponseRedirect(reverse('tmdb:school',
                    args=(new_school.slug,)))
    else:
        add_form = SchoolForm()
    context['add_form'] = add_form
    return render(request, template_name, context)

@permission_required("tmdb.change_school")
def school_change(request, school_slug):
    instance = get_object_or_404(models.School, slug=school_slug)
    template_name = 'tmdb/school_add_change.html'
    context = {}
    if request.method == 'POST':
        change_form = SchoolForm(request.POST, instance=instance)
        if change_form.is_valid():
            change_form.save()
            return HttpResponseRedirect(reverse('tmdb:school',
                    args=(school_slug,)))
    else:
        change_form = SchoolForm(instance=instance)
    context['change_form'] = change_form
    return render(request, template_name, context)

class SchoolDeleteForm(forms.ModelForm):
    class Meta:
        model = models.School
        fields = []

@permission_required("tmdb.delete_school")
def school_delete(request, school_slug):
    instance = get_object_or_404(models.School, slug=school_slug)
    template_name = 'tmdb/school_delete.html'
    context = {}
    if request.method == 'POST':
        delete_form = SchoolDeleteForm(request.POST, instance=instance)
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse('tmdb:schools'))
    else:
        delete_form = SchoolDeleteForm(instance=instance)
    context['delete_form'] = delete_form
    context['school'] = instance
    return render(request, template_name, context)
