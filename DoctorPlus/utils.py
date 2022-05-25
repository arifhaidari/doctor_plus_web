from cgitb import small
from appointment.models import Appointment, Feedback
from django.db.models import F
from datetime import date
import math

from user.models import FreeServiceSchedule


def star_out_of_five(doctor):
     feedback_object = Feedback.objects.filter(appointment__doctor=doctor)
     sum_of_stars = sum([item.score_count for item in feedback_object])
     feedback_no = feedback_object.count() or 0
     average_star = 3.5
     if sum_of_stars != 0 and feedback_no != 0:
          result = sum_of_stars/feedback_no
          average_star = "{:.1f}".format(result)
          average_star = float(average_star)
     return average_star, feedback_no



def is_valid_field_with_and(the_query_list):
    yes = True
    for query in the_query_list:
        if query != '' and query is not None:
            yes = False
    return yes

def is_valid_field_with_or(the_query_list):
     yes = True
     for query in the_query_list:
          if query == '' or query is None:
               yes = False
     print('value of yes', yes)
     return yes


def free_service_checker(doctor):
     # check if there is a free service 
     is_free_available = FreeServiceSchedule.objects.filter(doctor=doctor)
     if is_free_available.exists():
          free_service_obj = is_free_available.first()
          today_date = date.today()
          if free_service_obj.end_at <= today_date:
               is_free_available.delete()
               doctor.is_free_service = False
               doctor.save()
               doctor.refresh_from_db()

def evaluate_option(the_option):
     if Feedback.FeedbackOption.Better == the_option:
          return 1
     return 0

def evaluate_option_value(option_sum, feedback_no):
     result = (option_sum * 100) / feedback_no or 35.0
     result = "{:.2f}".format(result)
     result = float(result)
     return result or 35.0

def experience_year(doctor):
     today_date = date.today()
     all_experience = doctor.experience_set.all()
     year_number = 0
     try:
          if all_experience is not None:
               small_date = all_experience.first().start_date
               for experience in all_experience:
                    if small_date > experience.start_date:
                         small_date = experience.start_date
               the_difference = today_date - small_date
               year_number = the_difference.days / 365
     except:
          pass
     # the_year_final = 1 if math.ceil(year_number) == 0 else math.ceil(year_number)
     return math.ceil(year_number)

def calculate_patient_appt(doctor, operation='patient'):
     appt_object = Appointment.objects.filter(doctor=doctor)
     booked_appt_no = appt_object.filter(status=Appointment.ApptStatus.BOOKED).count() or 0
     completed_appt_no = appt_object.filter(status=Appointment.ApptStatus.COMPLETED).count() or 0
     my_patient_raw = (
          appt_object.filter(status=Appointment.ApptStatus.COMPLETED)
          .values(m_patient=F("patient__user"), m_relative=F("relative__user"))
          .distinct()
     )
     patient_no = my_patient_raw.count() or 0
     return completed_appt_no if operation == 'patient' else booked_appt_no, patient_no

def get_feedback_percentage(doctor):
     feedback_object = Feedback.objects.filter(appointment__doctor=doctor)
     average_star, feedback_no = star_out_of_five(doctor)
     completed_appt_no, patient_no = calculate_patient_appt(doctor)
     overall_experience = 35.0
     doctor_checkup = 35.0
     staff_behavior = 35.0
     clinic_environment = 35.0
     # get the percentage
     if feedback_no > 0:
          overall_sum = sum([evaluate_option(item.overall_experience) for item in feedback_object])
          overall_experience = evaluate_option_value(overall_sum, feedback_no)
          doctor_checkup_sum = sum([evaluate_option(item.doctor_checkup) for item in feedback_object])
          doctor_checkup = evaluate_option_value(doctor_checkup_sum, feedback_no)
          staff_behavior_sum = sum([evaluate_option(item.staff_behavior) for item in feedback_object])
          staff_behavior = evaluate_option_value(staff_behavior_sum, feedback_no)
          clinic_environment_sum = sum([evaluate_option(item.clinic_environment) for item in feedback_object])
          clinic_environment = evaluate_option_value(clinic_environment_sum, feedback_no)
     the_percentage = {
          'feedback_no': feedback_no,
          'average_star': average_star,
          'overall_experience': overall_experience,
          'doctor_checkup': doctor_checkup,
          'staff_behavior': staff_behavior,
          'clinic_environment': clinic_environment,
          'patient_no': patient_no,
          'completed_appt_no': completed_appt_no,
          'experience_year': experience_year(doctor),
          
     }
     return the_percentage
