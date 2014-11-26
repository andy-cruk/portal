from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from domain.models import CSADataFile


@login_required
def dashboard(request):
    if 'clear_cache' in request.GET:
        cache.clear()
        return redirect(dashboard)
    active_data_file = CSADataFile.objects.all().order_by('-updated').first()
    template_data = {
        'current_data_uploaded': active_data_file.updated if active_data_file else None,
        'analyzers': settings.CELL_SLIDER_ANALYSIS,
    }
    return render(request, 'cellsliderdata/pages/dashboard.html', template_data)













