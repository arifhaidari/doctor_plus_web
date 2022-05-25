from home.models import City
from user.models import (
    SpecialityCategory,
    Doctor,
    Speciality,
    Condition,
    Service,
    Patient,
)
from appointment.models import Feedback
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from doctor.models import Clinic, Disease, Symptoms
from itertools import chain
from patient.models import FavoriteDoctor
from appointment.models import Appointment
# from datetime import datetime
from django.db.models import Count


def home_view(request, *args, **kwargs):
    uzer = request.user
    if uzer.is_authenticated and not (13 >= len(uzer.phone) >= 10 and not any(c.isalpha() for c in uzer.phone)):
        # print("now it should redirect it --------- ")
        return redirect("user:social_adp")
    # print(" it should NOT redirect it --------- ")
    # if request.POST.get("searched-content") and request.POST.get("searched-content").isalnum():
    #     searched_content = request.POST.get("searched-content")
    #     name_searching = Q(user__full_name__icontains=searched_content) | Q(user__rtl_full_name__icontains=searched_content)
    #     phone_searching = Q(user__phone__icontains=searched_content)
    #     specialities = list(
    #         Speciality.objects.filter(
    #             Q(name__icontains=searched_content)
    #             | Q(farsi_name__icontains=searched_content)
    #             | Q(pashto_name__icontains=searched_content)
    #         )
    #         .distinct()
    #         .values("name")
    #     )
    #     doctors = list(
    #         Doctor.objects.filter(name_searching | phone_searching | Q(professional_status=2))
    #         .distinct()
    #         .values("user__full_name", "user__avatar")
    #     )
        
    #     return JsonResponse({"data": doctors, "speciality": specialities})
    provinces = City.objects.all()
    print('value fo provinces')
    print(len(provinces))
    context = {"speciality_categories": SpecialityCategory.objects.all(), 'provinces': provinces}
    return render(request, "home/homepage.html", context)


def search_view(request, *args, **kwargs):
    search_type = None
    gender_male = None
    gender_female = None
    category_id = None
    if request.method == "GET":
        if "searched-content" in request.session or "province" in request.session:
            searched_content = request.session.get("searched-content", "")
            province = request.session.get("province", 'all')
            
    if request.method == "POST":
        
        search_type = request.POST.get("search_type", None)
        searched_content = request.POST.get("searched-content") if request.POST.get("searched-content") else ""
        province = request.POST.get("province") if request.POST.get("province") else "all"
        request.session["searched-content"] = searched_content
        request.session["province"] = province
    
    # if search content is empty and province is all then we show the top 20 doctors of the country
    is_content_search = searched_content != '' and searched_content is not None
    clinic_doctors_id = []
    if is_content_search or province != 'all':
        print('contetn is may not be none or provicne is not all ---====-00====')
        clinic_filter = Q()
        if province != 'all':
            clinic_filter.add(Q(city__id=province), Q.OR)
            if is_content_search:
                clinic_filter.add(Q(clinic_name__icontains=searched_content) | Q(rtl_clinic_name__icontains=searched_content), Q.OR)
        else:
            clinic_filter.add(Q(clinic_name__icontains=searched_content) | Q(rtl_clinic_name__icontains=searched_content), Q.OR)
            
        clinics = Clinic.objects.filter(clinic_filter).values("doctor").distinct()
        clinic_doctors_id = [x.get("doctor") for x in clinics]
        # clinic_doctors = Doctor.objects.filter(user__id__in=clinic_doctors_id).filter(professional_status=True)
    
           
    final_filter = Q()
    if is_content_search:
        search_symptom = (
                Symptoms.objects.filter(
                    Q(name__icontains=searched_content)
                    |Q(farsi_name__contains=searched_content) 
                    |Q(pashto_name__contains=searched_content)).values("id").distinct()
            )
        
        search_disease = (
                Disease.objects.filter(
                    Q(name__icontains=searched_content) | Q(farsi_name__contains=searched_content) | Q(pashto_name__contains=searched_content) 
                    | Q(symptom__in=search_symptom)
                ).values("id").distinct()
            )

        specialities = Speciality.objects.filter(
            Q(name__icontains=searched_content)
            | Q(farsi_name__icontains=searched_content)
            | Q(pashto_name__icontains=searched_content)
            | Q(speciality_category__name__icontains=searched_content)
            | Q(speciality_category__farsi_name__contains=searched_content)
            | Q(speciality_category__pashto_name__contains=searched_content)
            | Q(disease__in=search_disease)
        ).distinct()
        
        
        services = Service.objects.filter(
            Q(name__icontains=searched_content)
            | Q(farsi_name__icontains=searched_content)
            | Q(pashto_name__icontains=searched_content)
        ).distinct()
        
        conditions = Condition.objects.filter(
            Q(name__icontains=searched_content)
            | Q(farsi_name__icontains=searched_content)
            | Q(pashto_name__icontains=searched_content)
        ).distinct()
        
        name_searching = Q(user__full_name__icontains=searched_content) | Q(user__rtl_full_name__icontains=searched_content)
        
        final_filter.add(Q(name_searching
            | Q(speciality__in=specialities)
            | Q(service__in=services)
            | Q(condition__in=conditions)
            ), Q.OR)
        
        
    
    if not is_content_search and province == 'all' and search_type == 'homepage':
        print('province is all and the content of search is emtpy')
        all_doctors = Doctor.objects.filter(professional_status=True).annotate(
                num_appts=Count('appointment', filter=Q(appointment__status=Appointment.ApptStatus.COMPLETED))
                ).order_by('-num_appts')[:20]
    else:
        if len(clinic_doctors_id) != 0:
            final_filter.add(Q(user__id__in=clinic_doctors_id), Q.OR)
        if search_type == 'search_page' and request.method == 'POST':
            print('value fo gender list 33333333')
            gender_male = request.POST.get('gender_male', None)
            gender_female = request.POST.get('gender_female', None)
            category_id = request.POST.get('speciality', None)
            
            if gender_female is not None and gender_male is None:
                final_filter.add(Q(user__gender='Female'), Q.AND)
            if gender_male is not None and gender_female is None:
                final_filter.add(Q(user__gender='Male'), Q.AND)
            
            print('valeu of category_id')
            print(category_id)
            if category_id is not None and category_id != 'all':
                final_filter.add(Q(speciality__speciality_category__id=category_id), Q.AND)
            
        
        all_doctors = Doctor.objects.filter(final_filter).filter(professional_status=True).distinct()

    # specialities and provicnes
    speciality_categories = SpecialityCategory.objects.all()
    provinces = City.objects.all()

    # paginator
    paginator = Paginator(all_doctors, 20)
    page = request.GET.get("page")
    all_doctors = paginator.get_page(page)
    

    data = {
        "doctors": all_doctors, 
        "speciality_categories": speciality_categories, 
        'provinces': provinces,
        'gender_male': gender_male,
        'gender_female': gender_female,
        'category_id': category_id,
        'searched_content': searched_content,
        'province_id': province,
        }
    return render(request, "home/search.html", data)


class DoctorProfileDetailView(generic.DetailView):
    model = Doctor
    context_object_name = "doctor"  # default is object
    template_name = "home/doctor/home_doctor_public_profile.html"

    def get_context_data(self, **kwargs):
        context = super(DoctorProfileDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            patient = get_object_or_404(Patient, user__id=self.request.user.id)
            fav = bool(FavoriteDoctor.objects.filter(patient=patient, doctor=self.object))
            data = {"is_your_fav_doc": fav}
            context.update(data)
        return context

    def post(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, user__id=self.request.user.id)
        if request.POST.get("add_to_fav"):
            _pateint_favs = FavoriteDoctor.objects.filter(patient=patient)
            if not _pateint_favs:
                _pateint_favs = FavoriteDoctor.objects.create(patient=patient)
            _pateint_favs[0].doctor.add(self.get_object())
            return JsonResponse({"status": "success"})
        if request.POST.get("rm_from_fav"):
            _pateint_favs = FavoriteDoctor.objects.get(patient=patient)
            _pateint_favs.doctor.remove(self.get_object())
            return JsonResponse({"status": "success"})

        return render(request, self.template_name, {})
