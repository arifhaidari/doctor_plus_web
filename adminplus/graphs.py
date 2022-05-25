from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count
from django.db.models import Q, F
from user.models import User, Doctor, Patient
from appointment.models import Appointment

is_adminplus_user = lambda request: request.user.user_type == User.Types.ADMINPLUS


@login_required
def dashboard_graph(request):
    doctors = Doctor.objects.filter(professional_status=True)
    doctors_by_province = doctors.values(province=F("user__address__city__name")).annotate(
        total=Count("user__address__city__name"),
        male=Count("user__gender", filter=Q(user__gender="Male")),
        female=Count("user__gender", filter=Q(user__gender="Female")),
        under_review=Count("is_profile_on_progress", filter=Q(is_profile_on_progress=True)),
    )
    patients_by_province = Patient.objects.values(city=F("user__address__city__name")).annotate(
        total=Count("user__address__city__name"),
        male=Count("user__gender", filter=Q(user__gender="Male")),
        female=Count("user__gender", filter=Q(user__gender="Female")),
    )
    completed_appointments_by_province = (
        Appointment.objects.filter(~Q(status=Appointment.ApptStatus.PENDING))
        .values(city=F("clinic__city__name"))
        .annotate(
            total=Count("clinic__city__name"),
            pending=Count("status", filter=Q(status=Appointment.ApptStatus.PENDING)),
            booked=Count("status", filter=Q(status=Appointment.ApptStatus.BOOKED)),
            completed=Count("status", filter=Q(status=Appointment.ApptStatus.COMPLETED)),
        )
    )

    print("from graphs")
    print(patients_by_province)
    context = {
        "name": "ali aref mohammadi",
        "doctors_by_province": {
            "labels": [x.get("province") for x in doctors_by_province],
            "count": [x.get("total") for x in doctors_by_province],
            "male": [x.get("male") for x in doctors_by_province],
            "female": [x.get("female") for x in doctors_by_province],
            "under_review": [x.get("under_review") for x in doctors_by_province],
        },
        "patients_by_province": {
            "labels": [x.get("city") for x in patients_by_province],
            "count": [x.get("total") for x in patients_by_province if x],
            "male": [x.get("male") for x in patients_by_province],
            "female": [x.get("female") for x in patients_by_province],
        },
        "compeleted_apps_by_province": {
            "labels": [x.get("city") for x in completed_appointments_by_province],
            "count": [x.get("total") for x in completed_appointments_by_province],
            "pending": [x.get("pending") for x in completed_appointments_by_province],
            "booked": [x.get("booked") for x in completed_appointments_by_province],
            "completed": [x.get("completed") for x in completed_appointments_by_province],
        },
    }
    return JsonResponse(context)

