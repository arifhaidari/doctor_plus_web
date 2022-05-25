from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404


def feedback_view(request, *args, **kwargs):
    patient_data = {}
    doctor_data = {}
    user_is = lambda user: request.user.user_type == user

    if user_is("PATIENT"):
        print("ppateni")
    elif user_is("DOCTOR"):
        print("doctor")

    doctor_view = render(request, "appointment/feedback/doctor.html", doctor_data)
    patient_view = render(request, "appointment/feedback/patient.html", patient_data)
    return patient_view if user_is("PATIENT") else doctor_view if user_is("DOCTOR") else Http404()
