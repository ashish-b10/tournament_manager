from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.urls import reverse
import django.forms

from datetime import date

from tmdb import forms, models

@permission_required('tmdb.add_season')
def season_add(request):
    template_name = 'tmdb/season_add_change.html'
    context = {}
    if request.method == 'POST':
        add_form = forms.SeasonAddChangeForm(request.POST)
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        today = date.today()
        start_date = date(year=today.year, month=9, day=1)
        if today < start_date:
            start_date = start_date.replace(year=start_date.year-1)
        add_form = forms.SeasonAddChangeForm(initial={
                'start_date': start_date,
                'end_date': start_date.replace(year=start_date.year+1),
        })
    context['add_form'] = add_form
    return render(request, template_name, context)

@permission_required("tmdb.change_season")
def season_edit(request, season_slug):
    instance = get_object_or_404(models.Season, slug=season_slug)
    template_name = 'tmdb/season_add_change.html'
    if request.method == "POST":
        change_form = forms.SeasonAddChangeForm(request.POST, instance=instance)
        if change_form.is_valid():
            change_form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        change_form = forms.SeasonAddChangeForm(instance=instance)
    context = {'change_form': change_form}
    return render(request, template_name, context)

@permission_required("tmdb.delete_season")
def season_delete(request, season_slug):
    instance = get_object_or_404(models.Season, slug=season_slug)
    template_name = 'tmdb/season_delete.html'
    context = {'season': instance}
    if request.method == "POST":
        delete_form = forms.SeasonDeleteForm(request.POST, instance=instance)
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        delete_form = forms.SeasonDeleteForm(instance=instance)
    context['delete_form'] = delete_form
    return render(request, template_name, context)
