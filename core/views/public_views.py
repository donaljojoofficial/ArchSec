from django.shortcuts import render
from django.views.decorators.cache import cache_page

from core.cache_utils import PUBLIC_PAGE_TIMEOUT


def landing_page(request):
    return render(request, "public/landing.html")


@cache_page(PUBLIC_PAGE_TIMEOUT)
def about_page(request):
    return render(request, "public/about.html")


def help_page(request):
    return render(request, "public/help.html")
