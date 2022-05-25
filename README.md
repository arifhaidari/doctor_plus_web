# API instructions

## General

_APIs you don't need to be athenticated to use them._

* ### Register New User
  * to register a new user use `user/api/auth/registration/` path, you have to fill 4fields, 

```
1- username (actually it takes the username and put it on our username field(phone field))
2- email
3- password1
4- password2
```
```jsonc
{
    "username": "",
    "email": "",
    "password1": "",
    "password2": ""
}
```

* ### Login User
  * to login with user use `user/api/token/` path, and fill two fields
  ```jsonc
    {
        "phone": "",
        "password": ""
    }
  ```

* ### Logout User
  * endpoint `/user/api/auth/logout/` This calls Django logout method and delete the Token object assigned to the current User object.


* ### change password
  * endpoint `/user/api/auth/password/change/`
  ```jsonc
    {
        "old_password": "",
        "new_password1": "",
        "new_password2": ""
    }
  ```

* ### Login Social Auth
  * @Facebook use the path `user/api/auth/facebook/` you have to pass either the access_token or code(we are using Access_Token)
  ```jsonc
    {
        "access_token": "",
        "code": "",
        "id_token": ""
    }
  ```

* ### Blogs
  * **List**: use the endpoint `/user/api/blog/`
  * **Search**: endpoints `/user/api/blog/?q=<key>` or `/user/api/blog/<post-id>/`
    * _icontains blog title_
    * _icontains blogger name(eng/fa)_
    * _iexact category name(eng/fa/pa)_
  * **Edit, Uppdate, Delete**: we don't need them here as an api.

* ### Relationships
  * **List**: `/user/api/relationship/` _list only endpoint_

* ### Blood
  * **List**: `/user/api/blood/` _list only endpoint_


* ### Search
  * **home search**: only return doctor, endpoint `/user/api/search/?q=<key>`
    * _by id_
    * _by name/rtl_name_
    * _by phone/email_
    * _by speciality (icontains)_
      * _name/farsi/pashto_
      * _category name/farsi/pashto_
    * _by condition (iexact name/farsi/pashto)_
    * _by service (iexact name/farsi/pashto)_
    * _by disiess (iexact name/farsi/pashto)_
    * _by symptoms (iexact name/farsi/pashto)_
  * **doctor public profile**: use endpoint `/user/api/search/<doctor-user-id>/`


## Doctor APIs

_you need to be authenticated as doctor to use these APIs._

* ### Doctor
  * **Update/Retrieve**(get, put, patch): Doctor profile endpoint `doctor/api/doctor/<your-id>/`, `<your-id>` current user id which should be a doctor.  


* ### Clinics
  * **List endpint** endpoint `doctor/api/clinic/`: all clinics
  * **Update/reterieve** endpoint `doctor/api/clinic/<clinic-id>/`: you must be the clinic owner to update it

* ### feedback
  * **List** endpoint `doctor/api/feedback/`
  * **Update/reterieve** endpoint `doctor/api/feedback/<feedback-id>/`

* ### feedback reply
  * **List** endpoint `doctor/api/feedback_reply/` 
  * **Update/reterieve** endpoint `doctor/api/feedback_reply/<feedback-id>/`

and the same for notification, medicalrecords, appointment, daypattren and deactivedslot
also  you as a doctor you have
mypatient and appointment-conditionthread endpoints too.


## Patient APIs

_you need to be authenticated a patient to use these APIs._

### Appointments
* List
  * endpoint `/patient/api/appointment/` lists all appointments of the current patient or for relative appointment use `/patient/api/appointment/?relative=<relative-id>`
  * SEARCH: filtering by doctor use `/patient/api/appointment/?doctor=<doctor-id>` (*doctor-id = doctor.user.id, relative-id = relative.user.id, ..*)

* Add appointment(book)
  * to book an appointment send post request to endpoint `/patient/api/appointment/` the post request should looks like this
  ```jsonc
    {
        "doctor": 1,
        "clinic": 5,
        "relative": 6,
        // relative is optional(if it was empty it will be booked for self)
        "appt_date": "2021-05-24",
        "start_appt_time": "07:30:00",
        "end_appt_time": "08:30:00"
    }
   ```

* Delete(actually it cancels the appointment here, instated of deleting the appointment)
  * endpoint `/patient/api/appointment/<appointment-id>/` if it's a relative appointment then `/patient/api/appointment/<appointment-id>/?relative=<relative-id>`

* Updating the appointment(Rescheduling)
  * Updating an appointment is **Not Allowed!** for a patient if in the case of he/she want to reschedule appointment. he/she has to delete the current appointment(*the delete cancels the appointment noting more*) and than, book a new appointment on empty appointment slots.


### Appointment Feedbacks
* **List**: endpoint `/patient/api/feedback/`
* **Details**: endpoint `/patient/api/feedback/<feedback-id>/`
* **Reply**
  * **Add**: to add reply use endpoint `/patient/api/feedback_reply/`
  ```jsonc
    {
        "feedback": "<feedback-id>",
        "reply": ""
    }
  ```
  * **Edit**: endpoint `patient/api/feedback_reply/<reply-id>/`
  ```jsonc
    {
        "reply": ""
    }
  ```
  * **Delete**: endpoint `patient/api/feedback_reply/<reply-id>/`



### Medicalrecords
* **List**: endpoint `patient/api/medicalrecord/` or `patient/api/medicalrecord/?relative=<relative-id>`
* **SEARCH**: if you want filter by doctor use `patient/api/medicalrecord/?doctor=<doctor-id>`

* **Add MedicalRecord**: endpoint `patient/api/medicalrecord/`
```jsonc
{
    "title": "",
    "relative": "<relative-id>", // optional
    "doctor": "<doctor-id>",
    "file": "<your-real-file>"
}
```

* **Edit MedicalRecord**: endpoint `patient/api/medicalrecord/<medicalrecord-id>` or `patient/api/medicalrecord/<medicalrecord-id>/?relative=<relative-id>`
```jsonc
{
    "title": "",
    "doctor": 1,
    "doctor_access": true,
    "general_access": true,
    "file": "<your-file>"
}
```

* **Delete MedicalRecord**: endpoint `/patient/api/medicalrecord/<medicalrecord-id>` or `patient/api/medicalrecord/<medicalrecord-id>/?relative=<relative-id>`


### Favorite Doctor
* **List**: endpoint `patient/api/favorite_doctor/`
* **Update**: endpoint `patient/api/favorite_doctor/<favorite-doctor-object-id>/`


### Relative
* **List**: endpoint `patient/api/relative/`

* **Add**: endpoint `patient/api/relative/`
```jsonc
{
    "user": {
        "full_name": "",
        "rtl_full_name": "",
        "avatar": "<file>", // optional
        "gender": "FEMALE",
        "phone": "",
    },
    "blood_group": "<id>",
    "rel": "<id>"
}
```

* **Edit**: endpoint `patient/api/relative/<relative-user-id>/`
* **Delete**: endpoint `patient/api/relative/<relative-user-id>/`

