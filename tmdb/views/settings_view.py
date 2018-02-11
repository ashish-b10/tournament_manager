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

def index(request):
    return HttpResponseRedirect(reverse('tmdb:tournaments'))

@permission_required("tmdb.change_configurationsetting")
def settings(request):
    return render(request, 'tmdb/settings.html')

@permission_required("tmdb.change_configurationsetting")
def registration_credentials(request):
    template_name = 'tmdb/configuration_setting.html'
    context = {"setting_name": "Registration Import Credentials"}
    setting_key = models.ConfigurationSetting.REGISTRATION_CREDENTIALS
    existing_setting = models.ConfigurationSetting.objects.filter(
            key=setting_key).first()
    if request.method == 'POST':
        form = forms.ConfigurationSetting(request.POST,
                instance=existing_setting)
        context['form'] = form
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        form = forms.ConfigurationSetting(initial={'key': setting_key,})
    context['form'] = form
    return render(request, 'tmdb/configuration_setting.html', context)

@permission_required("auth.add_user")
def create_headtable_user(request):
    template_name = 'tmdb/add_user.html'
    context = {}
    context['form_action'] = reverse('tmdb:create_headtable_user')
    if request.method == "POST":
        form = forms.UserForm(request.POST)
        context['form'] = form
        if form.is_valid():
            user = auth_models.User.objects.create_user(**form.cleaned_data)
            user.groups.set([get_headtable_permission_group()])
            return HttpResponseRedirect(reverse('tmdb:settings'))
    else:
        form = forms.UserForm()

    context['form'] = form
    context['user_type'] = "Head Table"
    return render(request, 'tmdb/add_user.html', context)

@permission_required("auth.add_user")
def create_ringtable_user(request):
    template_name = 'tmdb/add_user.html'
    context = {}
    context['form_action'] = reverse('tmdb:create_ringtable_user')
    if request.method == "POST":
        form = forms.UserForm(request.POST)
        context['form'] = form
        if form.is_valid():
            user = auth_models.User.objects.create_user(**form.cleaned_data)
            user.groups.set([get_ringtable_permission_group()])
            return HttpResponseRedirect(reverse('tmdb:settings'))
    else:
        form = forms.UserForm()

    context['form'] = form
    context['user_type'] = "Ring Table"
    return render(request, 'tmdb/add_user.html', context)

def get_ringtable_permission_group():
    group = auth_models.Group.objects.filter(name = "Ring Table").first()
    if not group:
        group = create_ringtable_permission_group()
    return group

def create_ringtable_permission_group():
    group = auth_models.Group.objects.create(name="Ring Table")
    group.permissions.set([auth_models.Permission.objects.get(
            name='Can change team match')])
    return group

def get_headtable_permission_group():
    group = auth_models.Group.objects.filter(name = "Head Table").first()
    if not group:
        group = create_headtable_permission_group()
    return group

def create_headtable_permission_group():
    group = auth_models.Group.objects.create(name="Head Table")
    group.permissions.set(auth_models.Permission.objects.filter(
            content_type__in=auth_models.ContentType.objects.filter(
                    app_label="tmdb")))
    group.permissions.add(auth_models.Permission.objects.get(
            name="Can add user"))
    return group
