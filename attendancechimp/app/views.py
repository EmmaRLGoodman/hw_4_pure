from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.models import User


from .models import StudentProfile, InstructorProfile

CDT = ZoneInfo("America/Chicago")


def time_view(request: HttpRequest) -> HttpResponse:
    """Return current Chicago time as HH:MM (24-hour), plain text."""
    now = datetime.now(tz=CDT)
    return HttpResponse(now.strftime("%H:%M"), content_type="text/plain")


def _decimal_to_str(x: Decimal) -> str:
    """Format Decimal without scientific notation and without trailing zeros."""
    s = format(x, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def sum_view(request: HttpRequest) -> HttpResponse:
    """Return n1 + n2 from query params as plain text."""
    n1_str = request.GET.get("n1", "0")
    n2_str = request.GET.get("n2", "0")

    try:
        val = Decimal(n1_str) + Decimal(n2_str)
    except (InvalidOperation, ValueError):
        return HttpResponse("Bad Request: n1 and n2 must be numbers", status=400, content_type="text/plain")

    return HttpResponse(_decimal_to_str(val), content_type="text/plain")

def index(request):
    time = time_view(request).content
    return render(request, 'app/index.html', {'time': time, 'user': request.user})

def new(request):
    if not request.method == "GET":
        return HttpResponse("Bad Request: New user template only accepts GET requests", status=405, content_type="text/plain")
    return render(request, 'app/new.html',{})

@csrf_exempt
def createUser(request):
    if not request.method == "POST":
        return HttpResponse("Bad Request: Create user template only accepts POST requests", status=405, content_type="text/plain")
    email = request.POST.get("email")
    user_name = request.POST.get("user_name")
    password = request.POST.get("password")
    is_student = request.POST.get("is_student")
    if User.objects.filter(email=email).exists():
        return HttpResponse("Bad Request: Email already in database", status=403, content_type="text/plain")
    my_user = User.objects.create_user(username = user_name,password = password,email = email)
    if is_student:
        StudentProfile(my_user)
    else:
        InstructorProfile(my_user)
    return render(request, 'app/createUser.html',{})