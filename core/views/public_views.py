from django.shortcuts import render


def landing_page(request):
    return render(request, "public/landing.html")


def about_page(request):
    return render(request, "public/about.html")


def help_page(request):
    return render(request, "public/help.html")
