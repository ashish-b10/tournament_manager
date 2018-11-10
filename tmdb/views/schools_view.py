from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required

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

@permission_required("tmdb.change_schoolseasonregistration")
def school_season_change(request, school_slug, season_slug):
    raise NotImplementedError()

@permission_required("tmdb.change_school")
def school_change(request, school_slug):
    raise NotImplementedError()
