from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import ProjectForm
from core.models.project import Project
from core.cache_utils import invalidate_user_cache

@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            # Extract and save structured data
            project.structured_data = form.get_structured_data()
            project.save()
            invalidate_user_cache(request.user.id)
            # form.save_m2m()  # If you had any many-to-many fields
            return redirect("dashboard")
    else:
        form = ProjectForm()

    return render(request, "core/create_project.html", {"form": form})
