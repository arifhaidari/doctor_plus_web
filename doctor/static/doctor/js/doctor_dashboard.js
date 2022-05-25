function cancel_appointment(app_id) {
  Swal.fire({
    title: 'Are you sure?',
    text: "You appiontment will be cacneled and other patient can book it!",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, Cancel it!'
  }).then((result) => {
    if (result.isConfirmed) {
      let form = new FormData();
      form.append("csrfmiddlewaretoken", csrftoken);
      form.append('cancel_appointment', app_id)
      axios.post(".", form).then((response) => {
        Swal.fire(
          'Appointment Canceled!',
          'Your file has been deleted.',
          'success'
        )
        $("tr[name='appoint_" + response.data.id + "']").addClass('canceld_appoinment')
        $("tr[name='appoint_" + response.data.id + "']").hide('slow')
      }).catch((error) => {
        console.error(error);
      });
    };
  });
};

console.log("dashboard is exxxxxxx")
// add appointment condition thread
function add_condition_thread(appid) {
  window.appid = appid;
  get_app_conditions();
  // $('#select-condition-thread').select2();
  $('#new-condition').hide('fast');
  $('#add-condition-thread').appendTo("body").modal('show');

}
$('#add-new-condition').click(function(event) {
  $('#new-condition').toggle('slow');
  $('#new_appointment_condition_thread_form').validate({
    submitHandler: function(form) {
      submit_new_appointment_condition_thread();
    },
    rules: {
      "farsi_name": "required",
      "pashto_name": "required",
    }
  });
});
$('#cancel-new-thread').click(function(event) {
  $('#new-condition').toggle('slow');
  $('#new_appointment_condition_thread_form').trigger("reset");
});
// submit new appointment condition thread
function submit_new_appointment_condition_thread() {
  let form = new FormData($('#new_appointment_condition_thread_form')[0]);
  form.append('new-condition', 1);
  axios.post("/doctor/addappthread/", form).then((response) => {
    if (response.data.status == "success") {
      location.reload();
    }
  }).catch((error) => {
    console.error(error);
  });
};
// submit appointment condition thread
$('#submit-appointment-thread').click(function(event) {
  let form = new FormData($("#submit-appointment-from")[0])
  form.append('appid', appid);
  axios.post(".", form).then((response) => {
    Swal.fire(
      'Condition Added!',
      'Appointment Condition Thread Added Successfully.',
      'success'
    );
  }).catch((error) => {
    console.error(error);
  });
});
// get appointment conditions
function get_app_conditions() {
  let form = new FormData();
  form.append('csrfmiddlewaretoken', csrftoken);
  form.append('app_conditions', 1);
  form.append('appid', appid);
  axios.post(".", form).then((response) => {
    let conditions = $("option[name='condition-thread-item']");
    $('#select-condition-thread').select2().val(response.data.conditions).trigger('change');
  }).catch((error) => {
    console.error(error);
  });
}