import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_headers

from .forms import AssignmentForm, StudentRegistrationForm
from .models import DUE_SOON, Assignment, Notice, Student

# Role-based access: only staff can create data; any logged-in user can read.
staff_required = user_passes_test(lambda u: u.is_authenticated and u.is_staff)

VALID_STATUSES = {"danger", "warning", "info", "success"}


def _is_htmx(request):
    """True for HTMX requests, but NOT for history-restore (back button) requests,
    which need the full page, not a fragment."""
    return (
        request.headers.get("HX-Request") == "true"
        and request.headers.get("HX-History-Restore-Request") != "true"
    )


def _toast(response, message, level="success", events=None):
    """Fire client-side events via the HX-Trigger response header.
    'show-toast' is picked up by the Alpine toast container in base.html."""
    payload = {"show-toast": {"message": message, "level": level}}
    payload.update(events or {})
    response["HX-Trigger"] = json.dumps(payload)
    return response


@login_required
def dashboard(request):
    now = timezone.now()
    pending = Assignment.objects.filter(due_date__gte=now)

    stats = {
        "total_students": Student.objects.count(),
        "pending_assignments": pending.count(),
        "due_soon": pending.filter(due_date__lt=now + DUE_SOON).count(),
        "recent_notices": Notice.objects.filter(posted_at__gte=now - timedelta(days=7)).count(),
    }

    # Dummy data for Chart.js — swap for real aggregates later.
    chart_data = {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "submissions": [12, 19, 8, 24, 31, 9, 14],
        "assigned": [15, 22, 14, 28, 33, 12, 16],
        "dept_labels": ["Computer Sci.", "Electronics", "Mechanical", "Civil", "Business"],
        "dept_counts": [120, 85, 64, 47, 90],
    }

    return render(request, "tracker/dashboard.html", {
        "stats": stats,
        "chart_data": chart_data,  # rendered with |json_script in the template
        "recent_notices": Notice.objects.all()[:5],
    })


@login_required
@vary_on_headers("HX-Request")  # keep caches from mixing fragment and full-page responses
def assignment_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    assignments = Assignment.objects.all()
    if q:
        assignments = assignments.filter(Q(title__icontains=q) | Q(course_code__icontains=q))
    if status in VALID_STATUSES:
        assignments = assignments.by_status(status)

    context = {"assignments": assignments, "q": q, "status": status}

    # HTMX search/filter requests only need the <tr> rows, not the whole page.
    if _is_htmx(request):
        return render(request, "tracker/partials/assignment_rows.html", context)

    if request.user.is_staff:
        context["form"] = AssignmentForm()
    return render(request, "tracker/assignment_list.html", context)


@staff_required
@require_http_methods(["POST"])
def assignment_create(request):
    form = AssignmentForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.save()
        msg = f"Assignment “{obj.title}” created."
        if _is_htmx(request):
            # Return a blank form + tell the table to refresh itself.
            response = render(request, "tracker/partials/assignment_form.html", {"form": AssignmentForm()})
            return _toast(response, msg, events={"assignments-changed": True})
        messages.success(request, msg)
        return redirect("tracker:assignment_list")

    if _is_htmx(request):
        # 200 (not 4xx) so HTMX swaps the form containing the validation errors.
        response = render(request, "tracker/partials/assignment_form.html", {"form": form})
        return _toast(response, "Please fix the highlighted errors.", "error")
    messages.error(request, "Could not create assignment. Please check the form.")
    return redirect("tracker:assignment_list")


@staff_required
@require_http_methods(["GET", "POST"])
def student_register(request):
    partial = "tracker/partials/student_form.html"

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.created_by = request.user
            student.save()
            msg = f"{student.full_name} ({student.roll_no}) registered successfully."
            if _is_htmx(request):
                return _toast(render(request, partial, {"form": StudentRegistrationForm()}), msg)
            messages.success(request, msg)
            return redirect("tracker:student_register")

        if _is_htmx(request):
            return _toast(render(request, partial, {"form": form}),
                          "Please fix the highlighted errors.", "error")
    else:
        form = StudentRegistrationForm()

    return render(request, "tracker/student_register.html", {"form": form})
