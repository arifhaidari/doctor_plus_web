from typing import List
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from DoctorPlus.utils import is_valid_field_with_or
from home.models import Address, City, District
from user.models import BloodGroup, Relative, RelativeRelation, User
from appointment.models import Appointment, ApptQrCode
from medicalrecord.models import MedicalRecords
from django.db.models import Q
# from . import forms
# from notification import patient_notifications as notification_manager


class RelativeList(ListView):
    model = Relative
    template_name = "relative/family_members.html"
    # add_user_form = forms.AddUserForRelativeForm()
    # add_relative_form = forms.AddRelativeForm()
    data = {
        "cities": City.objects.all(),
        "bloods": BloodGroup.objects.all(),
        "relations": RelativeRelation.objects.all(),
    }

    def get(self, request, *args, **kwargs):
        relatives = Relative.objects.filter(patient__user=request.user)
        self.data.update({"relatives": relatives})
        return render(request, self.template_name, self.data)

    def post(self, request, *args, **kwargs):
        # add_user_form = forms.AddUserForRelativeForm(request.POST, request.FILES or None)
        # add_relative_form = forms.AddRelativeForm(request.POST)
        print('value fo request.POST =====')
        the_status = 'success'
        print(request.POST)
        print('///////////////')
        print(request.FILES)
        try:
            if request.method == 'POST':
                data = request.POST
                patient = request.user.patient
                the_dict = dict(data)
                the_avatar = request.FILES.get('avatar', None)
                field_list = [value[0] for key, value in the_dict.items() if key != 'avatar']
                if is_valid_field_with_or(field_list):
                    print('all required fields are full')
                    is_phone = User.objects.filter(phone=data.get('phone'))
                    if not is_phone.exists():
                        same_name_filter = Q(Q(full_name=data.get('name')) | Q(rtl_full_name='rtl_name'))
                        is_same_name = User.objects.filter(same_name_filter)
                        if not is_same_name.exists():
                            relative_user = User.objects.create(
                                full_name=data.get('name'), rtl_full_name=data.get('rtl_name'), phone=data.get('phone'),
                                date_of_birth=data.get('dob'), gender=data.get('gender'), avatar=the_avatar, active=True,
                                user_type='Relative'
                            )
                            blood_group = BloodGroup.objects.get(id=data.get('blood_group'))
                            city = City.objects.get(id=data.get('city'))
                            district = District.objects.get(id=data.get('district'))
                            relation = RelativeRelation.objects.get(id=data.get('relation'))
                            relative_user.refresh_from_db()
                            # create address
                            Address.objects.create(
                                user=relative_user, city=city, district=district
                            )
                            # create relative
                            Relative.objects.create(
                                user=relative_user, blood_group=blood_group, relation=relation, patient=patient
                            )
                        else:
                            the_status = 'You have already a relative with this name, please try a different name or add aliases'
                    else:
                        the_status = 'Phone number already used in system, please try again different number'
                    
                else:
                    print('not full the required field')
                    the_status = 'Enter the info properly'
        except Exception as e:
            print('value of error')
            print(e)
            the_status = 'Unexpected error occured, please try again'
        return JsonResponse({'status': the_status})
        # return render(request, self.template_name, self.data)

class RelativeDetail(DetailView):
    model = Relative
    template_name = "relative/family_member_detail.html"
    data = {
        "cities": City.objects.all(),
        "bloods": BloodGroup.objects.all(),
        "relations": RelativeRelation.objects.all(),
    }

    def get(self, request, *args, **kwargs):
        relative = get_object_or_404(Relative, user__id=kwargs["pk"])
        appts = Appointment.objects.filter(patient__user=request.user, relative=relative)
        medicals = MedicalRecords.objects.filter(patient__user=request.user, relative=relative)
        data = {
            "relative": relative,
            "appointments": appts,
            "medicalrecords": medicals,
        }

        self.data.update(data)
        return render(request, self.template_name, self.data)

    def post(self, request, *args, **kwargs):
        print('value fo edit_family_member();')
        the_status = 'success'
        print(request.POST)
        print('////////////')
        print(request.FILES)
        is_error = False
        if request.POST.get('edit_form_data'):
            try:
                if request.method == 'POST':
                    data = request.POST
                    the_dict = dict(data)
                    the_avatar = request.FILES.get('avatar', None)
                    relative_id = kwargs.get('pk')
                    field_list = [value[0] for key, value in the_dict.items() if key != 'avatar']
                    if not is_valid_field_with_or(field_list):
                        the_status = 'Enter the info properly'
                        is_error = True
                    
                    is_users = User.objects.filter(phone=data.get('phone'))
                    if is_users.count() >= 1:
                        is_unique_phone = True
                        for  a_user in is_users:
                            if str(a_user.id) != relative_id:
                                is_unique_phone = False
                        if not is_unique_phone:
                            the_status = 'Phone number already used in system, please try again different number'
                            is_error = True
                            
                    if not is_error:
                        relative_user = User.objects.get(id=relative_id)
                        # update user
                        relative_user.full_name = data.get('name')
                        relative_user.rtl_full_name = data.get('rtl_name')
                        relative_user.phone = data.get('phone')
                        relative_user.date_of_birth = data.get('dob')
                        relative_user.gender = data.get('gender')
                        if the_avatar is not None:
                            relative_user.avatar = the_avatar
                        relative_user.save()
                        blood_group = BloodGroup.objects.get(id=data.get('blood_group'))
                        city = City.objects.get(id=data.get('city'))
                        district = District.objects.get(id=data.get('district'))
                        relation = RelativeRelation.objects.get(id=data.get('relation'))
                        relative_user.refresh_from_db()
                        # update address
                        address = relative_user.address
                        address.city = city
                        address.district = district
                        address.save()
                        # create relative
                        relative = relative_user.relative
                        relative.blood_group = blood_group
                        relative.relation = relation
                        relative.save()
                            
            except Exception as e:
                print('value of error')
                print(e)
                the_status = 'Unexpected error occured, please try again'
            return JsonResponse({"status": the_status})
        
        if request.POST.get("delete_family_member"):
            try:
                User.objects.filter(id=request.POST.get("delete_family_member")).delete()
            except:
                the_status = 'fail'
            return JsonResponse({"status": the_status})
        
        # delete medicalrecord
        if request.POST.get("delete_md"):
            get_object_or_404(MedicalRecords, id=request.POST.get("delete_md")).delete()
            return JsonResponse({"status": "success"})
        # general / doctor access changed
        if request.POST.get("toggle-action") == "on":
            instance = get_object_or_404(MedicalRecords, id=request.POST.get("file-id"))
            if request.POST.get("access_type") == "doc":
                instance.doctor_access = True
                instance.save()
            else:
                instance.general_access = True
                instance.save()
            return JsonResponse({"status": "success"})

        elif request.POST.get("toggle-action") == "off":
            instance = get_object_or_404(MedicalRecords, id=request.POST.get("file-id"))
            if request.POST.get("access_type") == "doc":
                instance.doctor_access = False
                instance.save()
            else:
                instance.general_access = False
                instance.save()
            return JsonResponse({"status": "success"})

        # appointment actions
        if request.POST.get("relative_cancel_app"):
            app = get_object_or_404(Appointment, id=request.POST.get("relative_cancel_app"))
            Appointment.objects.filter(id=request.POST.get("relative_cancel_app")).update(
                patient=None, relative=None, status=Appointment.ApptStatus.PENDING
            )
            # cancel appt notification 351_tackle
            # canceling the appointment
            app.status, app.patient, app.relative = "PENDING", None, None
            app.save()
            # deleting the Qr Code of appointment
            ApptQrCode.objects.filter(appt_slot=app).delete()
        elif request.POST.get("reschedule"):
            app = Appointment.objects.get(id=request.POST.get("reschedule"))
            avaliable_slots = Appointment.objects.filter(
                doctor=app.doctor,
                clinic=app.clinic,
                day_pattern=app.day_pattern,
                patient__isnull=True,
                status=Appointment.ApptStatus.PENDING,
                active=True,
            )
            avaliable = [
                {"id": x.id, "start": f"{x.start_appt_time}", "end": f"{x.end_appt_time}", "doctor_id": x.doctor.user.id}
                for x in avaliable_slots
            ]
            return JsonResponse({"avaliable_slots": avaliable})
        elif request.POST.get("commit-reschedule"):
            old = get_object_or_404(Appointment, id=request.POST.get("from_appointment"))
            new = get_object_or_404(Appointment, id=request.POST.get("to_appointment"))
            new.patient, new.relative, new.status = old.patient, old.relative, old.status
            old.patient, old.relative, old.status = None, None, Appointment.ApptStatus.PENDING
            get_object_or_404(ApptQrCode, appt_slot=old).delete()
            old.save()
            new.save()

        return render(request, self.template_name, self.data)

class ApptDetail(DetailView):
    template_name = 'relative/appt_detail.html'
    
    def get(self, request, *args, **kwargs):
        print('insdie the get of the deail')
        try:
            appt_id = kwargs.get('pk', None)
            print('value fo appt_id')
            print(appt_id)
            appt_object = Appointment.objects.get(id=appt_id)
        except:
            return HttpResponseNotFound()
        return render(request, self.template_name, {'appt_object': appt_object})
    


