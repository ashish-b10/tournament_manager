import json

from django.shortcuts import redirect, render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import models as auth_models
from django.contrib import messages

from tmdb import forms
from tmdb import models

from collections import defaultdict
import datetime

from tmdb.util.match_sheet import create_match_sheets
from tmdb.util.bracket_svg import SvgBracket

@permission_required("tmdb.add_competitor")
def competitor_add(request, tournament_slug, school_slug):
    template_name = 'tmdb/competitor_add_change.html'
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    competitors = models.Competitor.objects.filter(registration=school_registration)
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitors'] = competitors
    if request.method == 'POST':
        add_form = forms.SchoolCompetitorForm(request.POST)
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        add_form = forms.SchoolCompetitorForm(
                initial={'registration': school_registration})
    context['add_form'] = add_form
    return render(request, template_name, context)

@permission_required("tmdb.change_competitor")
def competitor_change(request, tournament_slug, school_slug, competitor_id):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    instance = models.Competitor.objects.get(pk = competitor_id)
    template_name = 'tmdb/competitor_add_change.html'
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitor'] = instance
    context['name'] = instance.name
    if request.method == 'POST':
        change_form = forms.SchoolCompetitorForm(request.POST,
                instance=instance)
        if change_form.is_valid():
            competitor = change_form.save()
            return HttpResponseRedirect(reverse('tmdb:tournament_school', args = (tournament_slug, school_slug)))
    else:
        change_form = forms.SchoolCompetitorForm(instance = instance)
        change_form.registration = school_registration
    context['change_form'] = change_form
    return render(request, template_name, context)

@permission_required("tmdb.delete_competitor")
def competitor_delete(request, tournament_slug, school_slug, competitor_id):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    instance = models.Competitor.objects.get(pk = competitor_id)
    template_name = 'tmdb/delete_competitor.html'
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitor'] = instance
    if request.method == 'POST':
        delete_form = forms.SchoolCompetitorDeleteForm(request.POST,
                instance=instance)
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        delete_form = forms.SchoolCompetitorDeleteForm(instance = instance)
    context['delete_form'] = delete_form
    return render(request, template_name, context)