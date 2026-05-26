from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from core.forms import ChatAnswerForm, DocumentIntakeForm, ProjectForm
from core.cache_utils import invalidate_user_cache
from core.models import SystemProfileDraft
from core.services.intake import (
    apply_chat_answer,
    calculate_missing_fields,
    extract_document_text,
    extract_profile_from_text,
    next_prompt_for_draft,
    profile_from_project_form,
    project_initial_from_profile,
)


@login_required
def intake_start(request):
    return render(request, "core/intake_start.html")


@login_required
def document_intake(request):
    if request.method == "POST":
        form = DocumentIntakeForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.cleaned_data["document"]
            try:
                extracted_text = extract_document_text(document)
                if not extracted_text.strip():
                    raise ValidationError("No readable text was found in that document.")
                collected_data, confidence = extract_profile_from_text(extracted_text)
            except ValidationError as exc:
                form.add_error("document", exc)
            else:
                document.seek(0)
                draft = SystemProfileDraft.objects.create(
                    user=request.user,
                    source="document",
                    uploaded_file=document,
                    original_filename=document.name,
                    extracted_text=extracted_text[:50000],
                    collected_data=collected_data,
                    confidence=confidence,
                    missing_fields=calculate_missing_fields(collected_data),
                    status="ready",
                )
                messages.success(request, "Document imported. Review the extracted system profile before saving.")
                return redirect("review_intake_draft", draft_id=draft.id)
    else:
        form = DocumentIntakeForm()

    return render(request, "core/document_intake.html", {"form": form})


@login_required
def chat_intake(request, draft_id=None):
    if draft_id:
        draft = get_object_or_404(SystemProfileDraft, id=draft_id, user=request.user, source="chat")
    else:
        draft = SystemProfileDraft.objects.create(
            user=request.user,
            source="chat",
            collected_data={"basic_info": {}, "structured_data": {}},
        )
        draft.missing_fields = calculate_missing_fields(draft.collected_data)
        draft.save()
        return redirect("chat_intake_draft", draft_id=draft.id)

    current_field, current_prompt = next_prompt_for_draft(draft)

    if request.method == "POST":
        if "review" in request.POST:
            draft.status = "ready"
            draft.save()
            return redirect("review_intake_draft", draft_id=draft.id)

        form = ChatAnswerForm(request.POST)
        if form.is_valid() and current_field:
            apply_chat_answer(draft, current_field, form.cleaned_data["answer"])
            return redirect("chat_intake_draft", draft_id=draft.id)
    else:
        form = ChatAnswerForm()

    return render(request, "core/chat_intake.html", {
        "draft": draft,
        "form": form,
        "current_field": current_field,
        "current_prompt": current_prompt,
        "can_review": bool((draft.collected_data or {}).get("basic_info")),
    })


@login_required
def review_intake_draft(request, draft_id):
    draft = get_object_or_404(SystemProfileDraft, id=draft_id, user=request.user)
    initial = project_initial_from_profile(draft.collected_data or {})

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.structured_data = form.get_structured_data()
            project.save()
            invalidate_user_cache(request.user.id)

            draft.project = project
            draft.status = "converted"
            draft.collected_data = profile_from_project_form(form)
            draft.missing_fields = []
            draft.save()

            messages.success(request, "System profile saved. You can run the modernization assessment now.")
            return redirect("dashboard")
    else:
        form = ProjectForm(initial=initial)

    return render(request, "core/review_intake.html", {
        "draft": draft,
        "form": form,
        "missing_fields": draft.missing_fields or [],
    })
