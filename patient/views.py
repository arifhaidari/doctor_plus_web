from ast import arg
from DoctorPlus.utils import star_out_of_five
from notification import notification_manager
from user.models import Patient, Relative, Doctor, BloodGroup
from appointment.models import Appointment, Feedback, FeedbackReplies, ApptQrCode
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseNotFound, JsonResponse
from django.http.response import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404, HttpResponseRedirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View

from django.db.models import Q, F

# from django.contrib.auth.forms import PasswordChangeForm
# from django.core.files.storage import FileSystemStorage
from . import forms
from notification.models import Notification
# from notification import patient_notifications as notification_manager

# from .forms import ChangePasswordForm
from medicalrecord import models as medicalrecord_models
from home.models import Address, City, District
from patient.models import FavoriteDoctor

User = get_user_model()


class FeedbackHandler(View):
    template_name = 'patient/feedback_handler.html'
    
    def get(self, request, *args, **kwargs):
        # get the doctor data and pass it on 
        print('value of kwargs')
        try:
            appt_id = kwargs.get('id', None)
            redirect_url = request.GET.get('q', None)
            print('value fo redirect_url');
            print(redirect_url)
            appt_object = Appointment.objects.get(id=appt_id)
            average_star, feedback_no = star_out_of_five(appt_object.doctor)
            context = {
                "doctor": appt_object.doctor, 
                'average_star': average_star, 
                'feedback_no': feedback_no,
                'appt_id': appt_id,
                'redirect_url': redirect_url,
                }
        except:
            return HttpResponseNotFound()
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        redirect_url = redirect(request.POST.get('redirect_url', None))
        if request.method == 'POST':
            try:
                data = request.POST
                appt_id = data.get('appt_id', None)
                redirect_url = data.get('redirect_url', None)
                appt_object = Appointment.objects.get(id=appt_id)
                Feedback.objects.create(
                    appointment = appt_object,
                    comment = data.get('review', None),
                    overall_experience = data.get('overall_experience', None),
                    doctor_checkup = data.get('doctor_checkup', None),
                    clinic_environment = data.get('clinic_environment', None),
                    staff_behavior = data.get('staff_behavior', None),
                )
                
                if appt_object.relative is not None:
                    redirect_url = redirect('relative:detail', pk=appt_object.relative.user.id)
                else:
                    redirect_url = redirect('patient:patient_dashboard_view')
                # create notification
                notification_manager.review_created_by_patient(appt_object, data['review'])
                # delete the notifiction
                Notification.objects.filter(appt=appt_object, category=Notification.Categories.review, receiver=request.user).delete()
                # 
            except Exception as e:
                redirect_url = redirect('patient:patient_dashboard_view')
                
        return redirect_url


def patient_dashboard_view(request, *args, **kwargs):
    try:
        user_is = lambda user: user == request.user.user_type
        if not user_is("Patient"):
            return HttpResponseForbidden()

        # form_new_comment = forms.CreateFeedbackForm()
        appointments = Appointment.objects.filter(patient__user=request.user, relative__isnull=True).order_by("-pk")
        medicalrecords = medicalrecord_models.MedicalRecords.objects.filter(
            patient=request.user.patient, relative__isnull=True
        ).order_by("-pk")

        if request.method == "POST":
            # delete medicalrecord
            if request.POST.get("delete_md"):
                get_object_or_404(medicalrecord_models.MedicalRecords, id=request.POST.get("delete_md")).delete()
                return JsonResponse({"status": "success"})
            # general / doctor access changed
            if request.POST.get("toggle-action") == "on":
                instance = get_object_or_404(medicalrecord_models.MedicalRecords, id=request.POST.get("file-id"))
                if request.POST.get("access_type") == "doc":
                    instance.doctor_access = True
                    instance.save()
                else:
                    instance.general_access = True
                    instance.save()
                return JsonResponse({"status": "success"})

            elif request.POST.get("toggle-action") == "off":
                instance = get_object_or_404(medicalrecord_models.MedicalRecords, id=request.POST.get("file-id"))
                if request.POST.get("access_type") == "doc":
                    instance.doctor_access = False
                    instance.save()
                else:
                    instance.general_access = False
                    instance.save()
                return JsonResponse({"status": "success"})

            # appiontment actions
            if request.POST.get("patient_cancel_app"):
                app = get_object_or_404(Appointment, id=request.POST.get("patient_cancel_app"))
                # sending the cancel notification to doctor
                # 351_tackle
                # canceling the appointment
                app.status, app.patient, app.relative = "PENDING", None, None
                app.save()
                # deleting the Qr Code of appointment
                ApptQrCode.objects.filter(appt_slot=app).delete()
                return JsonResponse({"status": "success"})
    except Exception as e:
        print('valur eof erorororo---===')
        print(e)
        return JsonResponse({"status": "fail"})

    
    data = {
        "appoinments": appointments,
        # "has_review": has_review,
        # "form_new_comment": form_new_comment,
        "medicalrecords": medicalrecords,
        # "add_medicalrecord_from": forms.AddMedicalRecordForm(user_id=request.user.id),
        # "edit_medicalrecord_from": forms.AddMedicalRecordForm(),
    }
    return render(request, "patient/dashboard.html", data)


class FavoriteDoctorListView(ListView):
    template_name = "patient/favorite_doctor.html"
    model = FavoriteDoctor

    def get_queryset(self):
        return FavoriteDoctor.objects.filter(patient=self.request.user.patient)

    def post(self, request, *args, **kwargs):
        print(request.POST)
        if request.POST.get("rm_from_fav"):
            _pateint_favs = FavoriteDoctor.objects.get(patient=request.user.patient)
            _pateint_favs.doctor.remove(get_object_or_404(Doctor, user_id=request.POST.get("rm_from_fav")))
            return JsonResponse({"status": "success", "id": request.POST["rm_from_fav"]})


class PatientProfileSetting(View):
    template_name = "patient/patient_profile_setting.html"
    data = {
        "selected_blood": "",
        "cities": City.objects.all(),
        "bloods": BloodGroup.objects.all(),
    }
    
    def get_data(self):
        user = self.request.user
        print("value of user inside the get_data")
        is_patient = Patient.objects.filter(user=user)
        if is_patient.exists():
            patient = is_patient.first()
            self.data.update({"selected_blood": patient.blood_group})
        return self.data

    def get(self, request, *args, **kwargs):
        get_dict = self.get_data()
        return render(request, self.template_name, get_dict)

    def post(self, request, *args, **kwargs):
        # get_dict = self.get_data()
        print("the post function got called ")
        if request.method == "POST":
            print("the method is POST")
            user = self.request.user
            is_patient = Patient.objects.filter(user=user)
            if is_patient.exists():
                patient = is_patient.first()
                save_patient_user(request.POST, user, patient)
                save_user_address(request.POST, user)
        return redirect("patient:patient_profile")


def save_patient_user(raw_data, user, patient):
    print("value fo save_patient_user")
    print(save_patient_user)
    user.full_name = raw_data.get("name")
    user.rtl_full_name = raw_data.get("rtl_name")
    user.date_of_birth = raw_data.get("dob")
    user.gender = raw_data.get("gender")
    user.save()
    patient.blood_group = BloodGroup.objects.get(id=raw_data.get("blood_group"))
    patient.save()


def save_user_address(raw_data, user):
    print("inside the save_patient_address")
    print('vlaue fo raw_data')
    print(raw_data)
    print('///////')
    print(raw_data)
    try:
        is_address = Address.objects.filter(user=user)
        if is_address.exists():
            address = is_address.first()
            address.user = user
            address.city = City.objects.get(id=raw_data.get("city"))
            address.district = District.objects.get(id=raw_data.get("district"))
            address.save()
        else:
            print('new address will be created ')
            new_address = Address(
                user=user,
                city=City.objects.get(id=raw_data.get("city")),
                district=District.objects.get(id=raw_data.get("district")),
            )
            new_address.save()
            print("saved the new address")
    except Exception as e:
        print('value fo error in save address')
        print(e)


def save_patient_avatar(request):
    user = request.user
    print("inside the save_patient_avatar")
    new_avatar = request.FILES.get("avatar")
    user_object = User.objects.get(phone=user.phone)
    if request.method == "POST":
        if user.avatar:
            user.avatar.delete()
            user_object.avatar = new_avatar
            user_object.save()
        else:
            user_object.avatar = new_avatar
            user_object.save()
    return HttpResponse("success")


class PatientPassword(PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = "patient/patient_change_password.html"


class PatientNotification(ListView):
    model = Notification
    context_object_name = "notifications"
    template_name = "patient/patient_notification.html"
    # ordering = ("-timestamp",)
    get_queryset = lambda self: Notification.objects.filter(receiver=self.request.user).order_by("-timestamp")

    # def get_context_data(self, **kwargs):
    #     context = super(PatientNotification, self).get_context_data(**kwargs)
    #     data = {
    #         # "chat_notifications": chat_notifications,
    #         # "feedback_notifications": feedback_notifications,
    #         # "appointment_notifications": appointment_notifications,
    #     }
    #     context.update(data)
    #     return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('clear_notification'):
            Notification.objects.filter(receiver=self.request.user).delete()
            return JsonResponse({'status': 'success'})
        return render(request, self.template_name, {})


def patient_review_view(request, *args, **kwargs):
    user_is = lambda user: request.user.user_type == user
    if not user_is("Patient"):
        return HttpResponseForbidden()
    appointment = get_object_or_404(Appointment, id=kwargs.get("appointment"), status="COMPLETED")
    comment = Feedback.objects.filter(appointment=appointment).exists()
    comment = Feedback.objects.get(appointment=appointment) if comment else create_feedback(appointment)
    rating_form = forms.FeedbackRatingForm(instance=comment)
    reply_form = forms.CreateFeedBackRepliesForm()
    if request.method == "POST":
        feedback = request.POST.get("appointment_feedbacked")
        if feedback:
            app = get_object_or_404(Appointment, id=feedback)
            app.feedback_status = True
            app.save()
            # deleting the notification (feedback this appointment)
            Notification.objects.get(category=1, feedback_doctor=app.doctor).delete()
            return JsonResponse({"status": "success"})
        if request.POST.get("overall_experience") is not None:
            rating_form = forms.FeedbackRatingForm(request.POST, instance=comment)
            if rating_form.is_valid():
                rating_form.save()
        if request.POST.get("submit") == "create-reply":
            replay = request.POST.get("reply")
            feedback_id = request.POST.get("comment-id")
            reply_form = forms.CreateFeedBackRepliesForm({"feedback": feedback_id, "author": request.user, "reply": replay})
            if reply_form.is_valid():
                reply_form.save()
                response = {
                    "status": "success",
                    "comment_id": feedback_id,
                    "reply": replay,
                    "user_pic": request.user.avatar.url,
                    "user_name": str(request.user),
                }
                # sending notification to doctor for patient replay
                # notification_manager.create_feedbackreplay_notification(feedback_id, replay)
                # review_relplied_by_doctor(appt_object, reply)
                return JsonResponse(response)

    data = {"appointment": appointment, "comment": comment, "rating_form": rating_form, "reply_form": reply_form}
    return render(request, "patient/dashboard/add_review.html", data)


def create_feedback(_appointment):
    Feedback(appointment=_appointment, comment="Comments Here.").save()
    return Feedback.objects.get(appointment=_appointment)
