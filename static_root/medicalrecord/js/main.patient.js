// console.log("PATIENT JS")
var loc = window.location;

var me = $("#myUsername").val();
var msg = $("#id_message");
var formData = $("#form-data");
var chatHolder = $("#chat-items");
var attachment = $("#chat-attachment");
var submitBtn = $("#submit-btn")
var checkbox = $(".checkbox-toggle")

//chat time
var time = new Date($.now());
var clear_time = time.toLocaleTimeString();

// submit action
submitBtn.click(function() {
  var file = attachment.prop("files")[0];
  var title = msg.val()
  var form = new FormData()
  form.append("csrfmiddlewaretoken", csrftoken);
  form.append("file", file)
  form.append("title", title)
  axios
    .post(".", form)
    .then(function(resp) {
      // console.log("resp data : ",resp.data)
      if (resp.data.status === "success") {
        socket.send(
          JSON.stringify({
            message: "attachment-file",
            title: title,
            files: resp.data.attachment,
          }));
      }
    })
    .catch(function(err) {
      alert("post err : ", err);
    });
  msg.text("")
})

// on attachment changed
attachment.change(function() { submitBtn.click() });
var c = $("#checkboxOneInput_default")

// on checkboxes changed
checkbox.change(function() {
  var color = $(this).css("background-color")
  if ($("input", this).is($("#checkboxOneInput_default"))) {
    if ($("input", this).prop("checked") == true) {
      checkbox.css('background-color', "#e0001a");
      $("label").css("left", "18px")
      var doctor_id = $(this).find('input[name="checkbox_doctor_id"]').val();
      var form = new FormData()
      form.append("csrfmiddlewaretoken", csrftoken);
      form.append("doctor_id", doctor_id)
      form.append("action", "deactive")
      axios
        .post(".", form)
        .then(function(resp) {
          if (resp.data.status === "success") {
            socket.send(
              JSON.stringify({
                message: "success",
                action: resp.data.action,
                doctor_id: doctor_id,
              })
            );
          }
        })
        .catch(function(err) { console.log("err : ", err) });
    } else {
      console.log("not checked pp")
      checkbox.css('background-color', "rgb(85, 206, 99)");
      $("label").css("left", "1px")
      var doctor_id = $(this).find('input[name="checkbox_doctor_id"]').val();
      var form = new FormData()
      form.append("csrfmiddlewaretoken", csrftoken);
      form.append("doctor_id", doctor_id)
      form.append("action", "active")
      axios
        .post(".", form)
        .then(function(resp) {
          if (resp.data.status === "success") {
            socket.send(
              JSON.stringify({
                message: "success",
                action: resp.data.action,
                doctor_id: doctor_id,
              })
            );
          }
        })
        .catch(function(err) { console.log("err : ", err) });
    }
  } else if (color == 'rgb(85, 206, 99)') {
    // when turns red
    $(this).css("background-color", "#e0001a");
    var doctor_id = $(this).find('input[name="checkbox_doctor_id"]').val();
    var form = new FormData()
    form.append("csrfmiddlewaretoken", csrftoken);
    form.append("doctor_id", doctor_id)
    form.append("action", "deactive")
    axios
      .post(".", form)
      .then(function(resp) {
        if (resp.data.status === "success") {
          socket.send(
            JSON.stringify({
              message: "success",
              action: resp.data.action,
              doctor_id: doctor_id,
            })
          );
        }
      })
      .catch(function(err) { console.log("err : ", err) });
  } else {
    // when turns green
    $(this).css("background-color", "#55ce63");
    var doctor_id = $(this).find('input[name="checkbox_doctor_id"]').val();
    var form = new FormData()
    form.append("csrfmiddlewaretoken", csrftoken);
    form.append("doctor_id", doctor_id)
    form.append("action", "active")
    axios
      .post(".", form)
      .then(function(resp) {
        if (resp.data.status === "success") {
          socket.send(
            JSON.stringify({
              message: "success",
              action: resp.data.action,
              doctor_id: doctor_id,
            })
          );
        }
      })
      .catch(function(err) { console.log("err : ", err) });
  }
})


// websocket
var wsStart = "ws://";
if (loc.protocol == "https:") {
  wsStart = "wss://";
}
var endpoint = wsStart + loc.host + loc.pathname;
var socket = new ReconnectingWebSocket(endpoint);
// var socket = new WebSocket(endpoint);

socket.onopen = function(e) {
  // console.log("open for", me, e);
  formData.submit(function(event) {
    event.preventDefault();
  });
};

socket.onmessage = function(e) {
  var chatDataMsg = JSON.parse(e.data);
  // console.log("message received from consumers : ", chatDataMsg)
  // console.log("chatDataMsg.user ", chatDataMsg.user)
  // console.log("me ", me)

  // sent the message
  if (chatDataMsg.user == me) {
    if (chatDataMsg.type === "img") {
      var sent_media = `<li class="media sent">
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="` + chatDataMsg.attachments + `" alt="Attachment">
                              <div class="chat-attach-caption">Image</div>
                              <a href="` + chatDataMsg.attachments + `" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        ` + chatDataMsg.title + `
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` + clear_time + `</span>
                            </div>
                          </li>
                        </ul>
                      </div>
                    </div>
                </div>
              </li>`
      chatHolder.append(sent_media);
    } else if (chatDataMsg.type === "att") {
      var sent_media = `<li class="media sent">
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="/static/img/file.jpg" alt="Attachment">
                              <div class="chat-attach-caption">Attachment</div>
                              <a href="` + chatDataMsg.attachments + `" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        ` + chatDataMsg.title + `
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` + clear_time + `</span>
                            </div>
                          </li>
                        </ul>
                      </div>
                    </div>
                </div>
              </li>`
      chatHolder.append(sent_media);
    }
  }
  // recevieing the message
  else {
    if (chatDataMsg.type === "img") {
      var receive_media = `<li class="media received">
                <div class="avatar">
                  <img src="` + chatDataMsg.user_avatar + `" alt="User Image" class="avatar-img rounded-circle">
                </div>
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-time">
                          <span>Patient ` + chatDataMsg.name + `</span>
                        </div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="` + chatDataMsg.attachments + `" alt="Attachment">
                              <div class="chat-attach-caption">Imagefile</div>
                              <a href="` + chatDataMsg.attachments + `" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        ` + chatDataMsg.title + `
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` + clear_time + `</span>
                            </div>
                          </li>
                        </ul>
                      </div>
                    </div>
                </div>
              </li>`
      chatHolder.append(receive_media);
    } else if (chatDataMsg.type === "att") {
      var receive_media = `<li class="media received">
                <div class="avatar">
                  <img src="` + chatDataMsg.user_avatar + `" alt="User Image" class="avatar-img rounded-circle">
                </div>
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-time">
                          <span>Patient ` + chatDataMsg.name + `</span>
                        </div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="/static/img/file.jpg" alt="Attachment">
                              <div class="chat-attach-caption">Attachment</div>
                              <a href="` + chatDataMsg.attachments + `" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        ` + chatDataMsg.title + `
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` + clear_time + `</span>
                            </div>
                          </li>
                        </ul>
                      </div>
                    </div>
                </div>
              </li>`
      chatHolder.append(receive_media);
    }
  }
};

socket.onerror = function(e) {
  console.log("error ", e);
};
socket.onclose = function(e) {
  console.log("close ", e);
};

// scroll to end of the chat
$(".chat-scroll").animate({ scrollTop: $(".chat-scroll")[0].scrollHeight * 1000 },
  "slow"
);