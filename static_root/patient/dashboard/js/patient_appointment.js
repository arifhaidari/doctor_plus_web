jQuery(document).ready(function($) {
  // go to feedback
  let go_to_review = $('a[name="go_to_review"]')
  go_to_review.click(function() {
    console.log("clicked !", $(this).attr('id'))
    let form = new FormData()
    form.append("csrfmiddlewaretoken", csrftoken);
    form.append('go_to_review', $(this).attr('id'))
    axios
      .post(".", form)
      .then(function(resp) {
        console.log("your request has successfully sent!")
      })
      .catch(function(err) { console.log("err : ", err) });
  });

  // * apponiment actions
  // cancel appointment
  $("a[name=cancel_appointment]").click(function(event) {
    appid = $(this).data("appid");
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
        form.append('patient_cancel_app', appid);
        axios.post(".", form).then((response) => {
          Swal.fire(
            'Successfully Canceled!',
            'Your appiontment has been canceled.',
            'success'
          );
        }).catch((error) => {
          console.error(error);
        });
      }
    });
  });

  // appointment rescheduling
  $("a[name='reschedule_appointment']").click(function(event) {
    
  });



  // ready function ended
});