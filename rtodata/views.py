from django.shortcuts import render


def dashboard(request):
    return render(request, 'rtodata/pages/dashboard.html')