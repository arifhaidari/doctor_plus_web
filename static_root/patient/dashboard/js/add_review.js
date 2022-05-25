jQuery(document).ready(function($) {

  var time = new Date($.now());
  var clear_time = time.toLocaleTimeString();

  // toggle reply box
  $(".card-body").hide()
  let reply = $('.comment-reply')
  reply.children('.comment-btn').click(function() {
    $(this).parent().find('.card-body').toggle()
  });


  // stars
  let empty_stars = $('div[name="bad-stars"]')
  let fill_stars = $('div[name="good-stars"]')

  // rating change actions
  function rating_change_action() {
    console.log("function changed!")
    console.log("function value :", $(this).val())
    console.log("function name :", $(this).attr('name'))

    if ($(this).val() == "GOOD") {
      form = $('#rating-changed').serialize()
      $(this).css('border-color', 'Green');
      fill_stars.append(`<i class="fas fa-star filled"></i>`)
      empty_stars.find('i')[0].remove()
      axios
        .post(".", form)
        .then(function(resp) {
          console.log("submited")
          if (resp.data.status == "success") {}
        })
        .catch(function(err) {
          console.log("err : ", err)
        });

    } else {
      form = $('#rating-changed').serialize()
      $(this).css('border-color', 'Red');
      empty_stars.append(`<i class="fas fa-star"></i>`)
      fill_stars.find('i')[0].remove()
      axios
        .post(".", form)
        .then(function(resp) {
          console.log("submited")

          if (resp.data.status == "success") {}
        })
        .catch(function(err) {
          console.log("err : ", err)
        });
    }
  };
  $('#id_doctor_checkup').change(rating_change_action);
  $('#id_staff_behavior').change(rating_change_action);
  $('#id_clinic_environment').change(rating_change_action);
  $("#id_overall_experience").change(rating_change_action);


  $('form[name="create-reply"]').submit(function(event) {
    event.preventDefault();
    axios
      .post(".", $(this).serialize())
      .then(function(resp) {
        if (resp.data.status == "success") {
          let new_reply = `<ul class="comments-reply">
										          <li>
										            <div class="comment">
										              <img class="avatar rounded-circle" alt="User Image" src="` + resp.data.user_pic + `">
										              <div class="comment-body w-100">
										                <div class="meta-data">
										                  <span class="comment-author">` + resp.data.user_name + `</span>
										                  <span class="comment-date">` + clear_time + `</span>
										                  <input type="hidden" name="replied" value="true">
										                </div>
										                <p class="comment-content">` + resp.data.reply + `</p>
										              </div>
										            </div>
										          </li>
										        </ul>`
          console.log("resp data ", resp.data)
          $("div[name='add-rep-" + resp.data.comment_id + "']").append(new_reply)

        }
      })
      .catch(function(err) {
        console.log("err : ", err)
      });
    $(this).find("textarea[name='reply']").val('')
    $(this).parent('.card-body').hide()
  });

  // ready function end
});

// submit your rating
function submit_rate(appointment_id) {
  var form = new FormData()
  form.append("csrfmiddlewaretoken", csrftoken);
  form.append('appointment_feedbacked', appointment_id);
  axios.post(".", form).then((response) => {
    if (response.data.status == "success") {
      $("div[name='feedback-now']").fadeOut('slow');
      Swal.fire({
        title: 'Thanks For Your Feedback!',
        text: 'Your feedback help others to find the correct doctor.',
        imageUrl: '/static/img/Thank-You-Letters.jpg',
        imageWidth: 450,
        imageHeight: 150,
        imageAlt: 'Custom image',
        confirmButtonText: "Close",
      })
    }
  }).catch((error) => {
    console.error(error);
  });
}
