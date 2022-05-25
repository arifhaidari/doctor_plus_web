from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.views.generic import (
    FormView,
    View,
    DetailView,
    ListView,
    TemplateView,
    CreateView,
    UpdateView,
)
from DoctorPlus.mixins import NextUrlMixin, RequestFormAttachMixin
from home.models import Address
from .forms import LoginForm, AdoptSocialUserForm

# from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from home.models import City, District
from user.models import Doctor, DoctorTitle, Patient

from allauth.socialaccount.models import SocialAccount

User = get_user_model()


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = "/"
    template_name = "user/login_page.html"
    default_next = "/"
    phone = ""
    password = ""

    def form_valid(self, form):
        self.phone = form.cleaned_data["phone"]
        self.password = form.cleaned_data["password"]
        return super().form_valid(form)
        # next_path = self.get_next_url()
        # return redirect(next_path)

    def get_success_url(self):
        next_path = self.get_next_url()
        qs = User.objects.filter(phone=self.phone, active=False)
        if qs.exists():
            if self.phone and self.password:
                data = {"phone": self.phone, "password": self.password}
                messages.info(
                    self.request,
                    "A user is already registered by this number but not verified. We have sent you token to verify your number",
                )
                return reverse_lazy("user:verify_user", kwargs={"dict": data})
        return f"{next_path}"


class PatientRegisterView(View):
    template_name = "user/patient_register.html"
    data = {
        "cities": City.objects.all(),
        # 'districts': District.objects.all(),
    }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.data)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            print("well the requst is the post")
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            city_id = request.POST.get("city")
            district_id = request.POST.get("district")
            gender = request.POST.get("gender")
            password = request.POST.get("password")
            credential = {"phone": phone, "password": password}
            if self.request.user.is_authenticated:
                messages.error(self.request, "There is a user already signed in")
                return redirect("home:homepage")
            deactivated_user = User.objects.filter(phone=phone, active=False)
            if deactivated_user.exists():
                messages.info(
                    request,
                    "A user is already registered by this number but not verified. We have sent you token to verify your number",
                )
                return redirect("user:verify_user", dict=credential)
            activated_user = User.objects.filter(phone=phone, active=True)
            if activated_user.exists():
                messages.error(
                    request,
                    "A user is already registered to this phone number. Try another number",
                )
                return redirect("user:patient_register")
            new_user = User.objects.create(full_name=name, phone=phone, gender=gender)
            new_user.set_password(password)
            new_user.save()
            Patient.objects.create(user=new_user)
            if city_id and district_id:
                city = City.objects.get(id=city_id)
                district = District.objects.get(id=district_id)
                Address.objects.create(user=new_user, city=city, district=district)
            return redirect("user:verify_user", dict=credential)
            # return reverse('user:verify_user', kwargs = {'dict': credential})
        return render(request, self.template_name, self.data)


class DoctorRegisterView(View):
    template_name = "user/doctor_register.html"
    data = {"doctor_titles": DoctorTitle.objects.all()}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.data)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            print("well the requst is the post")
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            title_id = request.POST.get("title")
            gender = request.POST.get("gender")
            email = request.POST.get("email")
            password = request.POST.get("password")
            credential = {"phone": phone, "password": password}
            if self.request.user.is_authenticated:
                messages.error(self.request, "There is a user already signed in")
                return redirect("home:homepage")
            deactivated_user = User.objects.filter(phone=phone, active=False)
            if deactivated_user.exists():
                messages.info(
                    request,
                    "A user is already registered by this number but not verified. We have sent you token to verify your number",
                )
                return redirect("user:verify_user", dict=credential)
            activated_user = User.objects.filter(phone=phone, active=True)
            if activated_user.exists():
                messages.error(
                    request,
                    "A user is already registered to this phone number. Try another number",
                )
                return redirect("user:doctor_register")
            email_available = User.objects.filter(email=email)
            if email_available.exists():
                messages.error(
                    request,
                    "This email is already exist in the system. Try another email address",
                )
                return redirect("user:doctor_register")
            new_user = User.objects.create(
                full_name=name,
                phone=phone,
                email=email,
                gender=gender,
                user_type=User.Types.Doctor,
            )
            new_user.set_password(password)
            new_user.save()
            if title_id:
                title = DoctorTitle.objects.get(id=title_id)
                Doctor.objects.create(user=new_user, title=title)
                print("doctor has been created")
            return redirect("user:verify_user", dict=credential)

        return render(request, self.template_name, self.data)


def load_districts(request):
    print("load_districts got called")
    city_id = request.GET.get("city_id")
    if city_id:
        districts = District.objects.filter(city_id=city_id)
        return render(request, "user/district_dropdown_list.html", {"districts": districts})
    else:
        return render(request, "user/district_dropdown_list.html", {})


def user_verify(request, dict):
    print("inside the user_veify")
    credential_dict = eval(dict)
    print(credential_dict)
    if request.method == "POST":
        token = request.POST.get("token")
        user = User.objects.get(phone=credential_dict["phone"])
        if user is not None:
            if token == "351351":
                messages.success(request, "User Successfully Activated")
                user.active = True
                user.save()
                return redirect("user:login")

        messages.error(request, "Token is incorrect")
        return render(request, "user/verify_user.html", credential_dict)

    return render(request, "user/verify_user.html", credential_dict)


class SocialAuthUserAdapter(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AdoptSocialUserForm
    template_name = "user/adopt_social_auth.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # adopting the user
        self.adopt_user(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        # setting user type
        self.object = self.get_object()
        self.object.user_type = request.POST.get("type").upper()
        self.object.save()
        # creating the user type instance
        if self.object.user_type == "Patient":
            Patient(user=self.object).save()
        elif self.object.user_type == "Doctor":
            Doctor(user=self.object).save()
        return super(self.__class__, self).post(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and self.valid_phone(self.request.user.phone):
            return redirect("home:homepage")
        # auths
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user == self.get_object():
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()

    def valid_phone(self, phone):
        return 13 >= len(phone) >= 10 and not any(c.isalpha() for c in phone)

    def get_object(self):
        return User.objects.get(pk=self.request.user.id)

    def adopt_user(self, user):
        sc_user = SocialAccount.objects.get(user=user)
        sc_data = sc_user.extra_data
        user.full_name = sc_data.get("name")
        sc_data.get("email") and user.__setattr__("email", sc_data["email"])
        sc_data.get("gender") and user.__setattr__("gender", sc_data["gender"].upper())
        if sc_data.get("birthday"):
            dob = sc_data["birthday"].split("/")
            dob = f"{dob[2]}-{dob[1]}-{dob[0]}"
            user.date_of_birth = dob

        # user.gender = sc_data.get("gender") or user.gender
        # user.avatar = sc_data["picture"]["data"]["url"] or sc_data.get("picture")
        user.save()
