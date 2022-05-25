console.log("DOCTOR JS")
var loc = window.location;

var me = $("#myUsername").val();
var msg = $("#id_message");
var formData = $("#form-data");
var chatHolder = $("#chat-items");
var currentChatHolderMessages = chatHolder.html()
var attachment = $("#chat-attachment");


//chat time
var time = new Date($.now());
var clear_time = time.toLocaleTimeString(); 

// on change actions
attachment.change(function () {
  var file = attachment.prop("files")[0];
  var title = msg.val()
  var form = new FormData()
  // console.log("file - ", file)
  form.append("csrfmiddlewaretoken", csrftoken);
  form.append("file", file)
  form.append("title", title)
  axios
    .post(".", form)
    .then(function (resp) {
      // alert("success!", resp.data)
      console.log("resp : ",resp)
      // console.log("resp data : ",resp.data)
      if (resp.data.status === "success") {
        socket.send(
          JSON.stringify({
            message: "attachment-file",
            title: title,
            files: resp.data.attachment,
          })
        );
      }
    })
    .catch(function (err) {
      alert("post err : ", err);
    });
    msg.text("")
});


// websocket
var wsStart = "ws://";
if (loc.protocol == "https:") {
  wsStart = "wss://";
}
var endpoint = wsStart + loc.host + loc.pathname;
var socket = new ReconnectingWebSocket(endpoint);
// var socket = new WebSocket(endpoint);

socket.onopen = function (e) {
  console.log("open for", me, e);
  formData.submit(function (event) {
    event.preventDefault();
    // var msgText = msg.val();
    // var finalData = {
    //   message: msgText,
    // };

    // if (msgText.trim()) {
    //   console.log("msg sent!");
    //   socket.send(JSON.stringify(finalData));
    //   formData[0].reset();
    // }
  });
};

socket.onmessage = function (e) {
  var chatDataMsg = JSON.parse(e.data);

  console.log("chatDataMsg: ", chatDataMsg)
  console.log("me :", me, " id :", chatDataMsg.id)

  // authorize and unauthorize doctors (to see patient shared files)
  if (chatDataMsg.action == "deactive" && me == chatDataMsg.id) {
    chatHolder.html("")
  } else if (chatDataMsg.action == "active" && me == chatDataMsg.id){
    chatHolder.html(currentChatHolderMessages)
  }

  if (chatDataMsg.user == me) {
    if (chatDataMsg.type === "img") {
      var sent_media = `<li class="media sent">
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="` + chatDataMsg.attachments +`" alt="Attachment">
                              <div class="chat-attach-caption">Image</div>
                              <a href="` + chatDataMsg.attachments +`" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        `+ chatDataMsg.title +`
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` +clear_time +`</span>
                            </div>
                          </li>
                        </ul>
                      </div>
                    </div>
                </div>
              </li>`
      chatHolder.append(sent_media);
    }
    else if(chatDataMsg.type === "att"){
      var sent_media = `<li class="media sent">
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="/static/img/file.jpg" alt="Attachment">
                              <div class="chat-attach-caption">Attachment</div>
                              <a href="` + chatDataMsg.attachments +`" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        `+ chatDataMsg.title +`
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` +clear_time +`</span>
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
                  <img src="`+ chatDataMsg.user_avatar +`" alt="User Image" class="avatar-img rounded-circle">
                </div>
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-time">
                          <span>Patient `+ chatDataMsg.name +`</span>
                        </div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="` + chatDataMsg.attachments +`" alt="Attachment">
                              <div class="chat-attach-caption">Imagefile</div>
                              <a href="` + chatDataMsg.attachments +`" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        `+ chatDataMsg.title +`
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` +clear_time +`</span>
                            </div>
                          </li>
                        </ul>
                      </div>
                    </div>
                </div>
              </li>`
    chatHolder.append(receive_media);
    }
    else if(chatDataMsg.type === "att"){
      var receive_media = `<li class="media received">
                <div class="avatar">
                  <img src="`+ chatDataMsg.user_avatar +`" alt="User Image" class="avatar-img rounded-circle">
                </div>
                <div class="media-body">
                    <div class="msg-box">
                      <div>
                        <div class="chat-time">
                          <span>Patient `+ chatDataMsg.name +`</span>
                        </div>
                        <div class="chat-msg-attachments">
                          <div class="chat-attachment">
                              <img src="/static/img/file.jpg" alt="Attachment">
                              <div class="chat-attach-caption">Attachment</div>
                              <a href="` + chatDataMsg.attachments +`" class="chat-attach-download">
                                <i class="fas fa-download"></i>
                              </a>
                          </div>
                        </div>
                        `+ chatDataMsg.title +`
                        <ul class="chat-msg-info">
                          <li>
                            <div class="chat-time">
                              <span>` +clear_time +`</span>
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

socket.onerror = function (e) {
  console.log("error ", e);
};
socket.onclose = function (e) {
  console.log("close ", e);
};

// scroll to end of the chat
$(".chat-scroll").animate(
  { scrollTop: $(".chat-scroll")[0].scrollHeight * 1000 },
  "slow"
);
