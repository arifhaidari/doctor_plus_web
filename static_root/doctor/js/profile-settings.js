// Add More Button Error
const addMoreClinicButtonError = document.getElementById('add_more_clinic_error');
const addMoreEducationButtonError = document.getElementById('add_more_education_error');
const addMoreExperienceButtonError = document.getElementById('add_more_experience_error');
const addMoreAwardButtonError = document.getElementById('add_more_award_error');



// Crop profile image and store it
const csrf = document.getElementsByName('csrfmiddlewaretoken')
$(document).ready(function() {
  var $modal = $('#crop_model');

  var image = document.getElementById('sample_image');

  var cropper;

  $('#upload_image').change(function(event) {
    var files = event.target.files;
    console.log(files)

    var done = function(url) {
      image.src = url;
      $modal.appendTo("body").modal('show');
    };

    if (files && files.length > 0) {
      reader = new FileReader();
      reader.onload = function(event) {
        done(reader.result);
      };
      reader.readAsDataURL(files[0]);
    }
  });

  $modal.on('shown.bs.modal', function() {
    cropper = new Cropper(image, {
      aspectRatio: 1,
      viewMode: 3,
      preview: '.preview'
    });
  }).on('hidden.bs.modal', function() {
    cropper.destroy();
    cropper = null;
  });



  $('#crop').click(function() {

    canvas = cropper.getCroppedCanvas({
      width: 300,
      height: 300
    });
    canvas.toBlob(function(blob) {
      url = URL.createObjectURL(blob);
      $('#uploaded_image').attr('src', url);
      ///////
      const fd = new FormData();
      fd.append('csrfmiddlewaretoken', csrf[0].value);
      fd.append('avatar', blob, 'doctor_avatar.png');

      $.ajax({
        type: 'POST',
        url: '/patient/avatar/',
        enctype: 'multipart/form-data',
        data: fd,
        success: function(response) {
          console.log('success', response)
        },
        error: function(error) {
          console.log('error', error)
        },
        cache: false,
        contentType: false,
        processData: false,
      })
      $modal.appendTo("body").modal('hide');
    });
  });
});

var inner_html_city_list = [];

$(document).ready(function() {
  var endPoint = "/doctor/json/city/";
  $.ajax({
    method: "GET",
    url: endPoint,
    success: function(data) {
      inner_html_city_list.push('<option value="">Select Province <span class="text-danger">*</span></option>');
      data.forEach(function(item, index) {
        inner_html_city_list.push('<option value="' + item['pk'] + '">' + item['fields']['name'] + ' - ' + item['fields']['rtl_name'] + '</option>');
      });
    },
    error: function(error_data) {
      console.log('error///////////////////'),
        console.log(error_data)
    }
  });
});


(function($) {
  "use strict";

  // Education Add More

  $(".education-info").on('click', '.trash', function() {
    $(this).closest('.education-cont').remove();
    return false;
  });

  $(".add-education").on('click', function() {
    const educations = document.getElementsByName('degree');
    console.log(educations.length);
    var educationLength = educations.length;
    if (educationLength < 10) {
      var educationcontent = '<div class="row form-row education-cont">' +
        '<div class="col-12 col-md-10 col-lg-11">' +
        '<div class="row form-row">' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Degree</label>' +
        '<input type="text" name="degree" id="degree" class="form-control">' +
        '<small id="degree_error" name="degree_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Degree (Farsi/Pashto)</label>' +
        '<input type="text" dir="rtl" name="rtl_degree" id="rtl_degree" class="form-control">' +
        '<small id="rtl_degree_error" name="rtl_degree_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>College/Institute</label>' +
        '<input type="text" name="school_name" id="school_name" class="form-control">' +
        '<small id="school_name_error" name="school_name_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>College/Institute (Farsi/Pashto)</label>' +
        '<input type="text" dir="rtl" name="rtl_school_name" id="rtl_school_name" class="form-control">' +
        '<small id="rtl_school_name_error" name="rtl_school_name_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Start Date</label>' +
        '<input type="date" name="school_start_date" id="school_start_date" class="form-control">' +
        '<small id="school_start_date_error" name="school_start_date_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>End Date</label>' +
        '<input type="date" name="school_end_date" id="school_end_date" class="form-control">' +
        '<small id="school_end_date_error" name="school_end_date_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
        '</div>' +
        '<hr>';
      $(".education-info").append(educationcontent);
    } else {
      console.log('valeu of educationLength in the somewhere');
      console.log(educationLength);
      addMoreEducationButtonError.innerHTML = "You are allowed to have 10 educations registered!";
      addMoreEducationButtonError.style.display = 'block';
    }
    return false;
  });

  // Experience Add More
  $(".experience-info").on('click', '.trash', function() {
    $(this).closest('.experience-cont').remove();
    return false;
  });

  $(".add-experience").on('click', function() {
    const experiences = document.getElementsByName('hospital_name');
    console.log(experiences.length);
    var experienceLength = experiences.length;
    if (experienceLength < 10) {
      var experiencecontent = '<div class="row form-row experience-cont">' +
        '<div class="col-12 col-md-10 col-lg-11">' +
        '<div class="row form-row">' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Hospital Name</label>' +
        '<input type="text" name="hospital_name" id="hospital_name" class="form-control">' +
        '<small id="hospital_name_error" name="hospital_name_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Hospital Name (Farsi/Pashto)</label>' +
        '<input type="text" dir="rtl" name="rtl_hospital_name" id="rtl_hospital_name" class="form-control">' +
        '<small id="rtl_hospital_name_error" name="rtl_hospital_name_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Designation</label>' +
        '<input type="text" name="designation" id="designation" class="form-control">' +
        '<small id="designation_error" name="designation_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Designation (Farsi/Pashto)</label>' +
        '<input type="text" dir="rtl" name="rtl_designation" id="rtl_designation" class="form-control">' +
        '<small id="rtl_designation_error" name="rtl_designation_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>From</label>' +
        '<input type="date" name="experience_start_date" id="experience_start_date" class="form-control">' +
        '<small id="experience_start_date_error" name="experience_start_date_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>To</label>' +
        '<input type="date" name="experience_end_date" id="experience_end_date" class="form-control">' +
        '<small id="experience_end_date_error" name="experience_end_date_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
        '</div>' +
        '<hr>';
      $(".experience-info").append(experiencecontent);
    } else {
      console.log('valeu of experienceLength in the somewhere');
      console.log(experienceLength);
      addMoreExperienceButtonError.innerHTML = "You are allowed to have 10 experiences registered!";
      addMoreExperienceButtonError.style.display = 'block';
    }
    return false;
  });

  // Awards Add More
  $(".awards-info").on('click', '.trash', function() {
    $(this).closest('.awards-cont').remove();
    return false;
  });

  $(".add-award").on('click', function() {
    const award = document.getElementsByName('award');
    console.log(award.length);
    var awardLength = award.length;
    if (awardLength < 15) {
      var regcontent = '<div class="row form-row awards-cont">' +
        '<div class="col-12 col-md-10 col-lg-11">' +
        '<div class="row form-row">' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Award</label>' +
        '<input type="text" name="award" id="award" class="form-control">' +
        '<small id="award_error" name="award_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Award (Farsi/Pashto)</label>' +
        '<input type="text" dir="rtl" name="rtl_award" id="rtl_award" class="form-control">' +
        '<small id="rtl_award_error" name="rtl_award_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-6 col-lg-4">' +
        '<div class="form-group">' +
        '<label>Date</label>' +
        '<input type="date" name="award_year" id="award_year" class="form-control">' +
        '<small id="award_year_error" name="award_year_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
        '</div>' +
        '<hr>';
      $(".awards-info").append(regcontent);
    } else {
      console.log('valeu of awardLength in the somewhere');
      console.log(awardLength);
      addMoreAwardButtonError.innerHTML = "You are allowed to have 15 experiences registered!";
      addMoreAwardButtonError.style.display = 'block';
    }
    return false;
  });

  // Clinic Add More
  $(".clinic-info").on('click', '.trash', function() {
    $(this).closest('.clinic-cont').remove();
    return false;
  });

  $(".add-clinic").on('click', function() {
    const clinics = document.getElementsByName('clinic_name');
    console.log('value of clinicLength');
    console.log(clinics.length);
    var clinicLength = clinics.length;
    if (clinicLength < 4) {
      var cliniccontent = '<div class="row form-row clinic-cont">' +
        '<div class="col-12 col-md-10 col-lg-11">' +
        '<div class="row form-row">' +
        '<div class="col-md-6">' +
        '<div class="form-group">' +
        '<label>Clinic Name <span class="text-danger">*</span></label>' +
        '<input type="text" name="clinic_name" id="clinic_name" class="form-control">' +
        '<small id="clinic_name_error" name="clinic_name_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-6">' +
        '<div class="form-group">' +
        '<label>Clinic Name (Farsi/Pashto)<span class="text-danger">*</span></label>' +
        '<input type="text" dir="rtl" name="rtl_clinic_name" id="rtl_clinic_name" class="form-control">' +
        '<small id="rtl_clinic_name_error" name="rtl_clinic_name_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-6">' +
        '<div class="form-group">' +
        '<label>Clinic Address<span class="text-danger">*</span></label>' +
        '<input type="text" class="form-control" id="clinic_address" name="clinic_address">' +
        '<small id="clinic_address_error" name="clinic_address_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-6">' +
        '<div class="form-group">' +
        '<label>Clinic Address (Farsi/Pashto) <span class="text-danger">*</span></label>' +
        '<input type="text" dir="rtl" class="form-control" id="rtl_clinic_address" name="rtl_clinic_address">' +
        '<small id="rtl_clinic_address_error" name="rtl_clinic_address_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-6">' +
        '<div class="form-group">' +
        '<select name="clinic_city" onchange="mySelectFunc(' + clinicLength + ');" id="clinic_city" class="form-control select clinic_city_class">' +
        '"' + inner_html_city_list + '"' +
        '</select>' +
        '<small id="clinic_city_error" name="clinic_city_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-6">' +
        '<div class="form-group">' +
        '<select name="clinic_district" id="clinic_district" class="form-control select">' +
        '<option value="">Select Province <span class="text-danger">*</span></option>' +
        '</select>' +
        '<small id="clinic_district_error" name="clinic_district_error" style="display: none;color: red;"></small>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
        '</div>' +
        '<hr>';
      $(".clinic-info").append(cliniccontent);
    } else {
      // show some error below the button
      console.log('valeu of clinic clinicLength in the somewhere');
      console.log(clinicLength);
      addMoreClinicButtonError.innerHTML = "You are allowed to have 4 clinics registered!";
      addMoreClinicButtonError.style.display = 'block';
    }
    return false;
  });

})(jQuery);



var isSaveError = false;
var isPreviewError = false;

function mySelectFunc(arg) {
  console.log('mySelectFunc is get called');
  var districtSelect = document.getElementsByName('clinic_district');
  var clinicCityList = document.getElementsByName('clinic_city');
  var endPoint = "/doctor/json/district/";
  $.ajax({
    url: endPoint,
    type: 'GET',
    data: {
      'city_id': clinicCityList[arg].value
    },
    success: function(data) {
      var inner_html_district_list = [];
      data.forEach(function(item, index) {
        console.log(item['fields']['name']);
        inner_html_district_list.push('<option value="' + item['pk'] + '">' + item['fields']['name'] + ' - ' + item['fields']['rtl_name'] + '</option>');
      });
      districtSelect[arg].innerHTML = inner_html_district_list;
    },
    error: function(error_data) {
      console.log('error///////////////////'),
        console.log(error_data)
    },
  });
};


// Basic Info
const doctorForm = document.getElementById('doctor_profile_form');
const fullName = document.getElementById('name');
const rtlName = document.getElementById('rtl_name');
const phone = document.getElementById('phone');
const email = document.getElementById('email');
const title = document.getElementById('title');
const licenseNo = document.getElementById('license_no');
const dob = document.getElementById('dob');

// Biography
const bio = document.getElementById('bio');
const bioFarsi = document.getElementById('bio_farsi');
const bioPashto = document.getElementById('bio_pashto');

// Contact Details
const city = document.getElementById('city');
const district = document.getElementById('district');

// Pricing
const fee = document.getElementById('fee');

// Services, Specialization and Condition
const specialist = document.getElementById('specialist');
const services = document.getElementById('services');
const conditions = document.getElementById('conditions');

// Buttons
const saveChangeButton = document.getElementById('save_change_button');
const submitPreviewButton = document.getElementById('submit_review_button');
const addMoreExperienceButton = document.getElementById('add_more_experience');
const addMoreEducationButton = document.getElementById('add_more_education');
const addMoreClinicButton = document.getElementById('add_more_clinic');

//////////////// Error displaying part //////////////////

// Basic Info Error
const nameError = document.getElementById('name_error');
const rtlNameError = document.getElementById('rtl_name_error');
const phoneError = document.getElementById('phone_error');
const emailError = document.getElementById('email_error');
const titleError = document.getElementById('title_error');
const licenseNoError = document.getElementById('license_no_error');
const dobError = document.getElementById('dob_error');

// Biography Error
const bioError = document.getElementById('bio_error');
const bioFarsiError = document.getElementById('bio_farsi_error');
const bioPashtoError = document.getElementById('bio_pashto_error');

// Contact Details Error
const cityError = document.getElementById('city_error');
const districtError = document.getElementById('district_error');

// Pricing Error
const feeError = document.getElementById('fee_error');

// Services, Specialization and Condition Error
const specialistError = document.getElementById('specialization_error');
const servicesError = document.getElementById('service_error');
const conditionsError = document.getElementById('condition_error');


$("#save_change_button").on('click', function() {
  console.log('saveChangeButton got pressed')
  doctorForm.addEventListener('submit', (e) => {
    console.log('the save change button got called');
    clinicFormValidation();
    educationFormValidation();
    experienceFormValidation();
    awardFormValidation();

    // Basic Info
    if (fullName.value.trim() === '' || fullName.value.trim() == null) {
      setError(fullName, nameError, 'Name field is emtpy');
    } else {
      if (!isNaN(fullName.value.trim())) {
        setError(fullName, nameError, 'Name must not be digits');
      }
    }
    if (rtl_name.value.trim() === '' || rtl_name.value.trim() == null) {
      setError(rtlName, rtlNameError, 'Name (Farsi/Pashto) field is emtpy')
    } else {
      if (!isNaN(rtlName.value.trim())) {
        setError(rtlName, rtlNameError, 'Name (Farsi/Pashto) must not be digits')
      }
    }
    if (phone.value.trim() === '' || phone.value.trim() == null) {
      setError(phone, phoneError, 'Phone number field is emtpy')
    } else {
      if (isNaN(phone.value)) {
        setError(phone, phoneError, 'Mobile numbers should be numbers only')
      } else if (phone.value.length != 10) {
        setError(phone, phoneError, 'Phone number should be 10 digits e.g. 077 xxxx xxx')
      } else if (phone.value < 0) {
        setError(phone, phoneError, 'Phone number should be positive numbers only')
      }
    }

    if (email.value.trim() === '' || email.value.trim() == null) {
      setError(email, emailError, 'Email field is emtpy')
    } else {
      if (!isNaN(email.value.trim())) {
        setError(email, emailError, 'Email must not be digits')
      }
      if (!validateEmail(email.value)) {
        setError(email, emailError, 'Email is not valid')
      }
    }

    if (title.value === '' || title.value == null) {
      setError(title, titleError, 'Title is not selected')
    }

    if (licenseNo.value.trim() === '' || licenseNo.value.trim() == null) {
      setError(licenseNo, licenseNoError, 'License No field is emtpy')
    }

    if (dob.value === '' || dob.value == null) {
      setError(dob, dobError, 'Date of Birth is empty')
    } else {
      var currentDate = new Date()
      let brith_date = String(dob.value).split("-")
      brith_date = new Date(brith_date[0], brith_date[1], brith_date[2])
      if (brith_date >= currentDate) {
        setError(dob, dobError, 'Birthday cannot be greater than current date')
      }

    }

    // Biography
    if (bio.value.trim() === '' || bio.value.trim() == null) {
      setError(bio, bioError, 'Bio field is emtpy')
    } else {
      if (!isNaN(bio.value.trim())) {
        setError(bio, bioError, 'Bio must not be digits')
      }
    }
    if (bioFarsi.value.trim() === '' || bioFarsi.value.trim() == null) {
      setError(bioFarsi, bioFarsiError, 'Bio (Pashto) field is emtpy')
    } else {
      if (!isNaN(bioFarsi.value.trim())) {
        setError(bioFarsi, bioFarsiError, 'Bio (Farsi) must not be digits')
      }
    }
    if (bioPashto.value.trim() === '' || bioPashto.value.trim() == null) {
      setError(bioPashto, bioPashtoError, 'Bio (Pashto) field is emtpy')
    } else {
      if (!isNaN(bioPashto.value.trim())) {
        setError(bioPashto, bioPashtoError, 'Bio (Pashto) must not be digits')
      }
    }

    // // Contact Details
    if (city.value === '' || city.value == null) {
      setError(city, cityError, 'Province is not selected')
    }

    if (district.value === '' || district.value == null) {
      setError(district, districtError, 'District is not selected')
    }

    // Pricing
    if (fee.value.trim() === '' || fee.value.trim() == null) {
      setError(fee, feeError, 'Fee field is emtpy')
    } else {
      if (isNaN(fee.value)) {
        setError(fee, feeError, 'Fee should be numbers only')
      } else if (fee.value < 0) {
        setError(fee, feeError, 'Fee should be positive numbers only')
      }
    }

    // Services, Specialization and Condition
    if (specialist.value.trim() === '' || specialist.value.trim() == null) {
      setError(specialist, specialistError, 'Specialization field is emtpy')
    }
    if (services.value.trim() === '' || services.value.trim() == null) {
      setError(services, servicesError, 'Services field is emtpy')
    }
    if (conditions.value.trim() === '' || conditions.value.trim() == null) {
      setError(conditions, conditionsError, 'Services field is emtpy')
    }

    if (isSaveError) {
      console.log('yes there is error')
      e.preventDefault()
      isSaveError = false
    }
    // check other part of the form here by calling the their functions
  })
})


function setError(inputField, errorArea, errorMessage) {
  isSaveError = true
  inputField.style.border = 'dashed 2px red'
  errorArea.innerHTML = errorMessage
  errorArea.style.display = 'block'
}

function validateEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
}
// Selecting districts by city
$("#city").change(function() {
  console.log('city has been changed')
  const url = $("#doctor_profile_form").attr("data-districts-url"); // get the url of the `load_districts` view
  const city_id = $(this).val(); // get the selected city ID from the HTML input
  $.ajax({ // initialize an AJAX request
    url: url, // set the url of the request (= /persons/ajax/load-cities/ )
    data: {
      'city_id': city_id // add the city id to the GET parameters
    },
    success: function(data) { // `data` is the return of the `load_districts` view function
      $("#district").html(data); // replace the contents of the district input with the data that came from the server
    }
  });
})
//


$("#specialist").change(function() {
  const url = $("#doctor_profile_form").attr("data-services-url");
  const specialities_id = $(this).val();
  speciality_list_id = JSON.stringify({
    'specialities_id': specialities_id
  })
  console.log("sp changed!")
  $.ajax({
    // contentType: 'application/json; charset=utf-8',
    // dataType: 'json',
    // type: 'GET',
    url: url,
    data: {
      'specialities_id': speciality_list_id,
    },
    success: function(data) {
      $("#services").html(data);
    }
  });
})
//

$("#specialist").change(function() {
  const url = $("#doctor_profile_form").attr("data-conditions-url");
  const specialities_id = $(this).val();
  speciality_list_id = JSON.stringify({
    'specialities_id': specialities_id
  })
  $.ajax({
    // contentType: 'application/json; charset=utf-8',
    // dataType: 'json',
    // type: 'GET',
    url: url,
    data: {
       'specialities_id': speciality_list_id,
    },
    success: function(data) {
      $("#conditions").html(data);
    }
  });
})


// commented by ali instated load_conditions defined on above
// $("#services").change(function() {
//   const url = $("#doctor_profile_form").attr("data-conditions-url");
//   const services_id = $(this).val();
//   service_list_id = JSON.stringify({
//     'services_id': services_id
//   })
//   $.ajax({
//     // contentType: 'application/json; charset=utf-8',
//     // dataType: 'json',
//     // type: 'GET',
//     url: url,
//     data: {
//       'services_id': service_list_id,
//       'specialities_id': speciality_list_id,

//     },
//     success: function(data) {
//       $("#conditions").html(data);
//     }
//   });
// })


function awardFormValidation() {
  console.log('value of awardFormValidation');
  const awardList = document.getElementsByName('award');
  awardList.forEach(function(item, i) {
    // Award
    const award = document.getElementsByName('award');
    const rtlAward = document.getElementsByName('rtl_award');
    const awardYear = document.getElementsByName('award_year');

    // // Award Error
    const awardError = document.getElementsByName('award_error');
    const rtlAwardError = document.getElementsByName('rtl_award_error');
    const awardYearError = document.getElementsByName('award_year_error');

    //  // // Validation part
    if (award[i].value.trim() === '' || award[i].value.trim() == null) {
      setError(award[i], awardError[i], 'Award field is emtpy')
    } else {
      if (!isNaN(award[i].value.trim())) {
        setError(award[i], awardError[i], 'Award must not be digits')
      }
    }
    if (rtlAward[i].value.trim() === '' || rtlAward[i].value.trim() == null) {
      setError(rtlAward[i], rtlAwardError[i], 'Award (Farsi/Pashto) field is emtpy')
    } else {
      if (!isNaN(rtlAward[i].value.trim())) {
        setError(rtlAward[i], rtlAward[i], 'Award (Farsi/Pashto) must not be digits')
      }
    }
    if (awardYear[i].value.trim() === '' || awardYear[i].value.trim() == null) {
      setError(awardYear[i], awardYearError[i], 'Award Date field is emtpy')
    } else {
      var currentDate = new Date();
      var award_date = String(awardYear[i].value).split("-")
      award_date = new Date(award_date[0], award_date[1], award_date[2])
      if (award_date > currentDate) {
        setError(awardYear[i], awardYearError[i], 'Award date cannot be in the future')
      }
    }
  });
}

function clinicFormValidation() {
  console.log('value of clinicFormValidation');
  const clinicList = document.getElementsByName('clinic_name');
  clinicList.forEach(function(item, i) {
    console.log('counter is running the loop in clinic')
    // Clinic Info
    var clinicName = document.getElementsByName('clinic_name');
    var rtlClinicName = document.getElementsByName('rtl_clinic_name');
    var clinicAddress = document.getElementsByName('clinic_address');
    var rtlClinicAddress = document.getElementsByName('rtl_clinic_address');
    var clinicCity = document.getElementsByName('clinic_city');
    var clinicDistrict = document.getElementsByName('clinic_district');
    // // Clinic Info Error
    var clinicNameError = document.getElementsByName('clinic_name_error');
    var rtlClinicNameError = document.getElementsByName('rtl_clinic_name_error');
    var clinicAddressError = document.getElementsByName('clinic_address_error');
    var rtlClinicAddressError = document.getElementsByName('rtl_clinic_address_error');
    var clinicCityError = document.getElementsByName('clinic_city_error');
    var clinicDistrictError = document.getElementsByName('clinic_district_error');

    // // Validation part
    if (clinicName[i].value.trim() === '' || clinicName[i].value.trim() == null) {
      setError(clinicName[i], clinicNameError[i], 'Clinic name field is emtpy')
    } else {
      if (!isNaN(clinicName[i].value.trim())) {
        setError(clinicName[i], clinicNameError[i], 'Clinic name must not be digits')
      }
    }
    if (rtlClinicName[i].value.trim() === '' || rtlClinicName[i].value.trim() == null) {
      setError(rtlClinicName[i], rtlClinicNameError[i], 'Clinic name (Farsi/Pashto) field is emtpy')
    } else {
      if (!isNaN(rtlClinicName[i].value.trim())) {
        setError(rtlClinicName[i], rtlClinicNameError[i], 'Clinic name (Farsi/Pashto) must not be digits')
      }
    }
    if (clinicAddress[i].value.trim() === '' || clinicAddress[i].value.trim() == null) {
      setError(clinicAddress[i], clinicAddressError[i], 'Clinic address field is emtpy')
    } else {
      if (!isNaN(clinicAddress[i].value.trim())) {
        setError(clinicAddress[i], clinicAddressError[i], 'Clinic address must not be digits')
      }
    }
    if (rtlClinicAddress[i].value.trim() === '' || rtlClinicAddress[i].value.trim() == null) {
      setError(rtlClinicAddress[i], rtlClinicAddressError[i], 'Clinic address (Farsi/Pashto) field is emtpy')
    } else {
      if (!isNaN(rtlClinicAddress[i].value.trim())) {
        setError(rtlClinicAddress[i], rtlClinicAddressError[i], 'Clinic address (Farsi/Pashto) must not be digits')
      }
    }
    if (clinicCity[i].value === '' || clinicCity[i].value == null) {
      setError(clinicCity[i], clinicCityError[i], 'Province is not selected')
    }

    if (clinicDistrict[i].value === '' || clinicDistrict[i].value == null) {
      setError(clinicDistrict[i], clinicDistrictError[i], 'District is not selected')
    }
  });
}

function experienceFormValidation() {
  console.log('value of experienceFormValidation');
  const experienceList = document.getElementsByName('hospital_name');
  experienceList.forEach(function(item, i) {
    // Experience
    const hospitalName = document.getElementsByName('hospital_name');
    const rtlHospitalName = document.getElementsByName('rtl_hospital_name');
    const designation = document.getElementsByName('designation');
    const rtlDesignation = document.getElementsByName('rtl_designation');
    const experienceStartDate = document.getElementsByName('experience_start_date');
    const experienceEndDate = document.getElementsByName('experience_end_date');

    // Experience Error
    const hospitalNameError = document.getElementsByName('hospital_name_error');
    const rtlHospitalNameError = document.getElementsByName('rtl_hospital_name_error');
    const designationError = document.getElementsByName('designation_error');
    const rtlDesignationError = document.getElementsByName('rtl_designation_error');
    const experienceStartDateError = document.getElementsByName('experience_start_date_error');
    const experienceEndDateError = document.getElementsByName('experience_end_date_error');

    // // Validation part
    if (hospitalName[i].value.trim() === '' || hospitalName[i].value.trim() == null) {
      setError(hospitalName[i], hospitalNameError[i], 'Hospital Name field is emtpy');
    } else {
      if (!isNaN(hospitalName[i].value.trim())) {
        setError(hospitalName[i], hospitalNameError[i], 'Hopital Name must not be digits');
      }
    }
    if (rtlHospitalName[i].value.trim() === '' || rtlHospitalName[i].value.trim() == null) {
      setError(rtlHospitalName[i], rtlHospitalNameError[i], 'Hospital Name (Farsi/Pashto) field is emtpy');
    } else {
      if (!isNaN(rtlHospitalName[i].value.trim())) {
        setError(rtlHospitalName[i], rtlHospitalNameError[i], 'Hospital Name (Farsi/Pashto) must not be digits');
      }
    }
    if (designation[i].value.trim() === '' || designation[i].value.trim() == null) {
      setError(designation[i], designationError[i], 'Designation field is emtpy');
    } else {
      if (!isNaN(designation[i].value.trim())) {
        setError(designation[i], designationError[i], 'Designation must not be digits');
      }
    }
    if (rtlDesignation[i].value.trim() === '' || rtlDesignation[i].value.trim() == null) {
      setError(rtlDesignation[i], rtlDesignationError[i], 'Designation (Farsi/Pashto) field is emtpy');
    } else {
      if (!isNaN(rtlDesignation[i].value.trim())) {
        setError(rtlDesignation[i], rtlDesignationError[i], 'Designation (Farsi/Pashto) must not be digits');
      }
    }
    if (experienceStartDate[i].value === '' || experienceStartDate[i].value == null) {
      setError(experienceStartDate[i], experienceStartDateError[i], 'Experience Start Date field is emtpy');
    } else {
      var currentDate = new Date()
      fromDate = Date(experienceStartDate[i].value)
      if (fromDate > currentDate) {
        setError(experienceStartDate[i], experienceStartDateError[i], 'Start date cannot be in the future');
      }
    }
    if (experienceEndDate[i].value === '' || experienceEndDate[i].value == null) {
      setError(experienceEndDate[i], experienceEndDateError[i], 'Experience End Date field is emtpy');
    } else {
      var currentDate = new Date();
      start_date = String(experienceStartDate[i].value).split("-")
      end_date = String(experienceEndDate[i].value).split("-")
      start_date = new Date(start_date[0], start_date[1], start_date[2])
      end_date = new Date(end_date[0], end_date[1], end_date[2])
      if (start_date > end_date) {
        setError(experienceEndDate[i], experienceEndDateError[i], 'Start date cannot be greater than end date');
      } else if (start_date > currentDate) {
        setError(experienceEndDate[i], experienceEndDateError[i], 'Start date cannot be greater than current date');
      }
    }
  });
}

function educationFormValidation() {
  console.log('value of experienceFormValidation');
  const educationList = document.getElementsByName('degree');
  educationList.forEach(function(item, i) {
    const degree = document.getElementsByName('degree');
    const rtlDegree = document.getElementsByName('rtl_degree');
    const schoolName = document.getElementsByName('school_name');
    const rtlSchoolName = document.getElementsByName('rtl_school_name');
    const schoolStartDate = document.getElementsByName('school_start_date');
    const schoolEndDate = document.getElementsByName('school_end_date');

    // Education Error
    const degreeError = document.getElementsByName('degree_error');
    const rtlDegreeError = document.getElementsByName('rtl_degree_error');
    const schoolNameError = document.getElementsByName('school_name_error');
    const rtlSchoolNameError = document.getElementsByName('rtl_school_name_error');
    const schoolStartDateError = document.getElementsByName('school_start_date_error');
    const schoolEndDateError = document.getElementsByName('school_end_date_error');

    // Validation part
    if (degree[i].value.trim() === '' || degree[i].value.trim() == null) {
      setError(degree[i], degreeError[i], 'Degree field is emtpy')
    } else {
      if (!isNaN(degree[i].value.trim())) {
        setError(degree[i], degreeError[i], 'Degree must not be digits')
      }
    }
    if (rtlDegree[i].value.trim() === '' || rtlDegree[i].value.trim() == null) {
      setError(rtlDegree[i], rtlDegreeError[i], 'Degree (Farsi/Pashto) field is emtpy')
    } else {
      if (!isNaN(rtlDegree[i].value.trim())) {
        setError(rtlDegree[i], rtlDegreeError[i], 'Degree (Farsi/Pashto) must not be digits')
      }
    }
    if (schoolName[i].value.trim() === '' || schoolName[i].value.trim() == null) {
      setError(schoolName[i], schoolNameError[i], 'School Name field is emtpy')
    } else {
      if (!isNaN(schoolName[i].value.trim())) {
        setError(schoolName[i], schoolNameError[i], 'School Name must not be digits')
      }
    }
    if (rtlSchoolName[i].value.trim() === '' || rtlDegree[i].value.trim() == null) {
      setError(rtlSchoolName[i], rtlSchoolNameError[i], 'School Name (Farsi/Pashto) field is emtpy')
    } else {
      if (!isNaN(rtlSchoolName[i].value.trim())) {
        setError(rtlSchoolName[i], rtlSchoolNameError[i], 'School Name (Farsi/Pashto) must not be digits')
      }
    }
    if (schoolStartDate[i].value === '' || schoolStartDate[i].value == null) {
      setError(schoolStartDate[i], schoolStartDateError[i], 'School Start Date field is emtpy')
    } else {
      var currentDate = new Date()
      fromDate = Date(schoolStartDate[i].value)
      if (fromDate > currentDate) {
        setError(schoolStartDate[i], schoolStartDateError[i], 'Start date cannot be in the future')
      }

    }
    if (schoolEndDate[i].value === '' || schoolEndDate[i].value == null) {
      setError(schoolEndDate[i], schoolEndDateError[i], 'School End Date field is emtpy')
    } else {
      var currentDate = new Date()
      var start_date = String(schoolStartDate[i].value).split("-")
      var end_date = String(schoolEndDate[i].value).split("-")
      start_date = new Date(start_date[0], start_date[1], start_date[2])
      end_date = new Date(end_date[0], end_date[1], end_date[2])
      if (start_date > end_date) {
        setError(schoolEndDate[i], schoolEndDateError[i], 'Start date cannot be greater than end date')
      } else if (start_date > currentDate) {
        setError(schoolEndDate[i], schoolEndDateError[i], 'Start date cannot be greater than current date')
      }
    }
  });
}