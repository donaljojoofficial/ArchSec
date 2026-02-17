# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import ProjectAnalysis


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optional: Log the user in immediately after registration
            login(request, user)
            return redirect('dashboard') # Redirect to your main page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def view_diagrams(request, analysis_id):
    analysis = get_object_or_404(ProjectAnalysis, id=analysis_id)
    return render(request, 'core/view_diagrams.html', {'analysis': analysis})
