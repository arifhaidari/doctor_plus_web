jQuery(document).ready(function($) {

  var time = new Date($.now());
  var clear_time = time.toLocaleTimeString();

  // toggle reply box
  $(".card-body").hide()
  let reply = $('.comment-reply')
  reply.children('.comment-btn').click(function() {
    $(this).parent().find('.card-body').toggle()
  });

  $('form[name="create-reply"]').submit(function(event) {
    event.preventDefault();

    console.log("submission cancelled")
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
          // $("li[name='comment_"+ resp.data.comment_id+"']").append(new_reply)
          $("div[name='add-rep-" + resp.data.comment_id + "']").append(new_reply)

        }
      })
      .catch(function(err) { console.log("err : ", err) });
    $(this).find("textarea[name='reply']").val('')
    $(this).parent('.card-body').hide()
    // $(this).parent('.card-body').parent('.comment-reply').hide();


  });




  // ready.function end!
});