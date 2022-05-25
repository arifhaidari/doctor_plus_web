console.log("relative js file !")

jQuery(document).ready(function($) {
  // go to feedback
  // let go_to_review = $('a[name="go_to_review"]')
  // go_to_review.click(function() {
  //   console.log("clicked !", $(this).attr('id'))
  //   let form = new FormData()
  //   form.append("csrfmiddlewaretoken", csrftoken);
  //   form.append('go_to_review', $(this).attr('id'))
  //   axios
  //     .post(".", form)
  //     .then(function(resp) {
  //       console.log("your request has successfully sent!")
  //     })
  //     .catch(function(err) { console.log("err : ", err) });
  // });
  
  // apponiment actions
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

        console.log('i am in here bro .....==----');
        document.getElementById('appt_' + appid).style.display = 'none';
        let form = new FormData();
        form.append("csrfmiddlewaretoken", csrftoken);
        form.append('relative_cancel_app', appid);
        axios.post(".", form).then((response) => {
          console.log('it is working dude ')
          if (response.data.status === "success") {
            console.log('it is working dude =========')
          Swal.fire(
            'Successfully Canceled!!!!!!',
            'Your appiontment has been canceled.',
            'success'
          );

          $("tr[name='appt_" + appid + "']").remove()
          }
          
        }).catch((error) => {
          console.log('the erororororo')
          console.error(error);
        });
      }
    });
  });

  // appointment rescheduling
  $("a[name='reschedule_appointment']").click(function(event) {
    let form = new FormData();
    form.append("csrfmiddlewaretoken", csrftoken);
    form.append('reschedule', $(this).data("appid"));
    axios.post(".", form).then(async (response) => {
      times = {}
      let avaliable_slots = response.data.avaliable_slots;
      for (x of avaliable_slots) {
        times[x.id] = `${x.start} - ${x.end}`;
      }
      // console.log(" the final one looks : ", times)
      const { value: new_app } = await Swal.fire({
        inputPlaceholder: 'Reschedule',
        title: 'Select New Timing',
        input: 'select',
        inputOptions: {
          "Booked Day": times,
          "Change Day": {
            "other_day": "Select other day"
          }
        },
        showCancelButton: true,
      })
      // when ok is clicked
      if (new_app) {
        // Swal.fire(`You selected: ${new_time}`)
        console.log("the new_app is ", new_app)
        if (new_app === "other_day") {
          let form = new FormData();
          form.append("csrfmiddlewaretoken", csrftoken);
          form.append('patient_cancel_app', $(this).data("appid"));
          axios.post(".", form).then((resp) => {}).catch((error) => { console.error(error); });
          location.href = `/appoint/appt/${response.data.avaliable_slots[0].doctor_id}/`
        } else {
          Swal.fire({
            title: 'Reschedule?',
            text: "Your current appointment will be reschedule and others may book it!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, Reschedule!'
          }).then((result) => {
            if (result.isConfirmed) {
              let form = new FormData();
              form.append("csrfmiddlewaretoken", csrftoken);
              form.append("commit-reschedule", "true");
              form.append('from_appointment', $(this).data("appid"));
              form.append('to_appointment', new_app);
              axios.post(".", form).then((response) => {
                Swal.fire(
                  'Done!',
                  'Appointment successfully rescheduled.',
                  'success'
                )
                location.reload()
              }).catch((error) => {});
            }
          })
        } // end of if-else
      } // end of if new_app
    }).catch((error) => {
      console.error(error);
    });

  });

  // ready function ended
});
