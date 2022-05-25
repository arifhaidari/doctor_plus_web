from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseNotFound, JsonResponse, Http404
from django.views.generic import View, DetailView
from DoctorPlus.utils import is_valid_field_with_or
from appointment.models import Appointment
from user.models import Patient, Relative
from django.contrib import messages
from user.models import Doctor
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .models import MedicalRecordFile, MedicalRecords
from django.contrib.auth import get_user_model

User = get_user_model()


class AddMedicalRecord(View):
     template_name = 'medicalrecord/add_medical_record.html'
     
     def get_data(self, patient):
          relatives = Relative.objects.filter(patient=patient)
          the_filter = Q(Q(status=Appointment.ApptStatus.COMPLETED) | Q(status=Appointment.ApptStatus.BOOKED))
          doctor_id_collection = patient.appointment_set.filter(the_filter).values_list('doctor__user__id', flat=True).distinct()
          # users = User.objects.filter(id__in=doctor_id_collection)
          doctors = Doctor.objects.filter(user__id__in=doctor_id_collection)
          return {
                    'relatives': relatives,
                    'doctors': doctors,
               }
     
     def get(self, request, *args, **kwargs):
          print('insdie the get of the deail')
          try:
               patient = request.user.patient
               the_context = self.get_data(patient)
          except:
               return HttpResponseNotFound()
          return render(request, self.template_name, the_context)
     
     def post(self, request, *args, **kwargs):
          print('inside the post method ===-000-=====')
          try:
               patient = request.user.patient
               the_files = request.FILES.getlist('medical_documents', None)
               data = request.POST
               the_dict = dict(data)
               field_list = [value[0] for value in the_dict.values()]
               if is_valid_field_with_or(field_list):
                    relative = None
                    share_to_all = True
                    if data.get('sharing_policy', None) == 'share_with_selected':
                         share_to_all = False
                    if data.get('patient') != str(patient.user.id):
                         relative = Relative.objects.get(user__id=data.get('patient'))
                    related_doctor = Doctor.objects.get(user__id=data.get('related_doctor'))
                    medical_object = MedicalRecords.objects.create(
                         title=data.get('title', None), patient = patient, relative=relative, 
                         related_doctor=related_doctor, general_access=share_to_all
                    )
                    shared_with_list = data.getlist('shared_with', None)
                    if shared_with_list is not None and len(shared_with_list) != 0:
                         medical_object.refresh_from_db()
                         for _id in shared_with_list:
                              doc_obj = Doctor.objects.get(user__id=_id)
                              medical_object.shared_with.add(doc_obj)
                    if the_files is not None and len(the_files) != 0:
                         for a_file in the_files:
                              MedicalRecordFile.objects.create(
                                   medical_record = medical_object, file=a_file
                              )    
          except:
               if request.user.is_authenticated:
                    the_context = self.get_data(patient)
                    messages.error(self.request, "Unexpected error occured, Please enter your info properly")
                    return render(request, self.template_name, the_context)
               else:
                    return HttpResponseNotFound()
               
          the_context = self.get_data(patient)
          return render(request, self.template_name, the_context)
          # return redirect('')


class EditMedicalRecord(View):
     template_name = 'medicalrecord/edit_medical_record.html'
     
     def get_data(self, patient, medical_id):
          relatives = Relative.objects.filter(patient=patient)
          the_filter = Q(Q(status=Appointment.ApptStatus.COMPLETED) | Q(status=Appointment.ApptStatus.BOOKED))
          doctor_id_collection = patient.appointment_set.filter(the_filter).values_list('doctor__user__id', flat=True).distinct()
          doctors = User.objects.filter(id__in=doctor_id_collection)
          medical_object = MedicalRecords.objects.get(id=medical_id)
          medical_patient = patient
          if medical_object.relative is not None:
               medical_patient = medical_object.relative
          return {
                    'relatives': relatives,
                    'doctors': doctors,
                    'medical_object': medical_object,
                    'medical_patient': medical_patient.user,
               }
     
     def get(self, request, *args, **kwargs):
          print('insdie the get of the deail')
          try:
               medical_id = kwargs.get('id', None)
               print('value fo appt_id')
               print(medical_id)
               patient = request.user.patient
               the_data = self.get_data(patient, medical_id)
          except:
               return HttpResponseNotFound()
          return render(request, self.template_name, the_data)
     
     def post(self, request, *args, **kwargs):
          # if medical record count is zero and there is nothing in the file field and asked for adding it 
          # but save other attribute like titles 
          print('in post of edit bro')
          try:
               patient = request.user.patient
               if not request.POST.get('delete_medical_file'):
                    print(request.POST)
                    print('//////')
                    print(request.FILES)
                    medical_id = kwargs.get('id', None)
                    print('value fo appt_id')
                    print(medical_id)
                    the_files = request.FILES.getlist('medical_documents', None)
                    data = request.POST
                    the_dict = dict(data)
                    field_list = [value[0] for value in the_dict.values()]
                    if is_valid_field_with_or(field_list):
                         relative = None
                         share_to_all = True
                         if data.get('sharing_policy', None) == 'share_with_selected':
                              share_to_all = False
                         if data.get('patient') != str(patient.user.id):
                              relative = Relative.objects.get(user__id=data.get('patient'))
                         related_doctor = Doctor.objects.get(user__id=data.get('related_doctor'))
                         medical_object = MedicalRecords.objects.get(id=medical_id)
                         medical_object.title = data.get('title', None)
                         medical_object.relative = relative
                         medical_object.related_doctor = related_doctor
                         medical_object.general_access = share_to_all
                         medical_object.save()
                         # sharing with doctors
                         shared_with_list = data.getlist('shared_with', None)
                         medical_object.refresh_from_db()
                         if shared_with_list is not None and len(shared_with_list) != 0:
                              medical_object.shared_with.clear()
                              for _id in shared_with_list:
                                   doc_obj = Doctor.objects.get(user__id=_id)
                                   medical_object.shared_with.add(doc_obj)
                         else:
                              medical_object.shared_with.clear()
                         if the_files is not None and len(the_files) != 0:
                              for a_file in the_files:
                                   MedicalRecordFile.objects.create(
                                        medical_record = medical_object, file=a_file
                                   ) 
                    else:
                         messages.error(request, 'Unknown error occured, please try again')
                         return render(request, self.template_name, the_data)
               if request.POST.get('delete_medical_file'):
                    medical_file_id = request.POST.get('delete_medical_file')
                    MedicalRecordFile.objects.filter(id=medical_file_id).delete()
                    return JsonResponse({"status": "success"})
               the_data = self.get_data(patient, medical_id)
          except Exception as e:
               print('value of ther erorororororor====')
               print(e)
               return HttpResponseNotFound()
          return redirect(request.POST.get('redirect_url'))


class MeicalRecordDetail(DetailView):
    template_name = 'medicalrecord/medical_record_detail.html'
    
    def get(self, request, *args, **kwargs):
        print('insdie the get of the deail')
        if not request.user.is_authenticated:
          return HttpResponseForbidden()
        try:
            medical_id = kwargs.get('pk', None)
            print('value fo appt_id')
            print(medical_id)
            medical_object = MedicalRecords.objects.get(id=medical_id)
        except:
            return HttpResponseNotFound()
        return render(request, self.template_name, {'medical_object': medical_object})

# @login_required
# def file_sharing_view(request, *args, **kwargs):
#     doctor_data = {}
#     patient_data = {}
#     pagenation_perlist = 5
#     user_is = lambda user: request.user.user_type == user

#     if user_is("PATIENT"):
#         main_patient = get_object_or_404(FileSharingPatient, patient__user=request.user, relative=None)
#         relatives = get_list_or_404(Relative, patient__patient=main_patient)
#         appointments = get_list_or_404(Appointment, patient__user=request.user)
#         medicalrecords = get_list_or_404(MedicalRecords.objects.order_by("-timestamp"), patient__patient__user=request.user)
#         appointment_doctors = Appointment.objects.filter(patient__user=request.user).values("doctor").distinct()
#         forms = [UpdateMedicalRecordForm(instance=x) for x in medicalrecords]
#         paginator = Paginator(medicalrecords, pagenation_perlist)
#         page = request.GET.get("page")
#         medicalrecords = paginator.get_page(page)

#         if request.method == "POST":
#             submit = request.POST.get("submit")
#             submit_new_record, submit_update, submit_delete = "new-record", "update", "delete"
#             if submit:
#                 if submit == submit_delete:
#                     get_object_or_404(MedicalRecords, id=request.POST.get("file-id")).delete()
#                     return JsonResponse({"status": "success", "deleted_id": request.POST.get("file-id")})
#                 elif submit == submit_update:
#                     from_instace = UpdateMedicalRecordForm(
#                         request.POST,
#                         request.FILES,
#                         instance=get_object_or_404(MedicalRecords, id=request.POST.get("file-id")),
#                     )
#                     if from_instace.is_valid():
#                         from_instace.save()
#                         new_title = get_object_or_404(MedicalRecords, id=request.POST.get("file-id")).title
#                         return JsonResponse(
#                             {"status": "success", "updated_id": request.POST.get("file-id"), "title": new_title}
#                         )

#                 elif submit == submit_new_record:
#                     from_instace = CreateMedicalRecordForm(
#                         request.POST or None,
#                         request.FILES or None,
#                         # initial={"patient": request.user.id},
#                         user_id=request.user.id,
#                     )
#                     if from_instace.is_valid():
#                         from_instace.save()
#                         messages.success(request, "Medicalrecord added!")
#                         from_instace = UpdateMedicalRecordForm()

#             # toggle button action
#             if request.POST.get("toggle-action") == "on":
#                 instance = get_object_or_404(MedicalRecords, id=request.POST.get("file-id"))
#                 if request.POST.get("access_type") == "doc":
#                     instance.doctor_access = True
#                     instance.save()
#                 else:
#                     instance.general_access = True
#                     instance.save()
#                 return JsonResponse({"status": "success"})

#             elif request.POST.get("toggle-action") == "off":
#                 instance = get_object_or_404(MedicalRecords, id=request.POST.get("file-id"))
#                 if request.POST.get("access_type") == "doc":
#                     instance.doctor_access = False
#                     instance.save()
#                 else:
#                     instance.general_access = False
#                     instance.save()
#                 return JsonResponse({"status": "success"})

#         patient_data = {
#             "patient": main_patient,
#             "relatives": relatives,
#             "appointments": appointments,
#             "appointment_doctors": appointment_doctors,
#             "medicalrecords": medicalrecords,
#             "forms": forms,
#             "form": CreateMedicalRecordForm(user_id=request.user.id),
#         }

#     elif user_is("DOCTOR"):
#         main_doctor = get_object_or_404(Doctor, user=request.user)
#         patients = list(Appointment.objects.filter(doctor=main_doctor).values("patient"))
#         patients = [x.get("patient") for x in patients]
#         medicalrecords = get_list_or_404(
#             MedicalRecords.objects.order_by("-timestamp"),
#             (
#                 (Q(doctor=main_doctor) & Q(doctor_access=True))
#                 | (Q(patient__patient__in=patients) & Q(general_access=True, doctor_access=True))
#             ),
#         )
#         paginator = Paginator(medicalrecords, pagenation_perlist)
#         page = request.GET.get("page")
#         medicalrecords = paginator.get_page(page)

#         doctor_data = {
#             "main_doctor": main_doctor,
#             "medicalrecords": medicalrecords,
#         }

#     doctor_view = render(request, "medicalrecord/doctor.html", doctor_data)
#     patient_view = render(request, "medicalrecord/patient.html", patient_data)
#     return patient_view if user_is("PATIENT") else doctor_view if user_is("DOCTOR") else Http404()


