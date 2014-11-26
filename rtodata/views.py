from django.conf import settings
from django.shortcuts import render, redirect
from django.core.cache import cache



def dashboard(request):
    if 'clear_cache' in request.GET:
        cache.clear()
        return redirect(dashboard)
    active_data_file = None
    template_data = {
        'current_data_uploaded': active_data_file.updated if active_data_file else None,
        'analyzers': settings.RTO_ANALYSIS,
    }
    return render(request, 'rtodata/pages/dashboard.html', template_data)
