// add medicalrecord
$("#addmdform").toggle('fast');
$("#addmdform").validate({
  rules: {
    "doctor": "required",
    "title": "required",
    "file": {
      required: true,
    }
  }
});




// delete medicalrecord
function delete_medical_record(md_id) {
  console.log("delete this id ", md_id)
  Swal.fire({
    title: 'Are you sure?',
    text: "You won't be able to revert this!",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!'
  }).then((result) => {
    if (result.isConfirmed) {
      let form = new FormData()
      form.append("csrfmiddlewaretoken", csrftoken);
      form.append('delete_md', md_id)
      axios.post(".", form).then((response) => {
        if (response.data.status === "success") {
          Swal.fire(
            'Deleted!',
            'Your file has been deleted.',
            'success'
          )
          $("tr[name='record_" + md_id + "']").remove()
        }
      }).catch((error) => {
        console.error(error);
      })
    }
  })
}

// changing access of a medical reocrd
var checkbox = $(".checkbox-toggle")
checkbox.change(function() {
  var file_id = $(this).find('input[name="file-id"]').val();
  var access_type = $(this).find('input[name="access_type"]').val(); // it's "gen" or "doc"

  // console.log("color : ",$(this).css('background-color'))
  if ($(this).css('background-color') == "rgb(224, 0, 26)") {
    $(this).css('background-color', "rgb(85, 206, 99)");
    $("label", this).css("left", "1px");
    form = new FormData()
    form.append("csrfmiddlewaretoken", csrftoken);
    form.append('file-id', file_id);
    form.append('toggle-action', 'on');
    form.append('access_type', access_type);
    axios
      .post(".", form)
      .then(function(resp) {
        if (resp.data.status === "success") {}
      })
      .catch(function(err) { console.log("err : ", err) });
  } else {
    $(this).css('background-color', "rgb(224, 0, 26)");
    $("label", this).css("left", "18px")
    form = new FormData()
    form.append("csrfmiddlewaretoken", csrftoken);
    form.append('file-id', file_id);
    form.append('toggle-action', 'off')
    form.append('access_type', access_type);
    axios
      .post(".", form)
      .then(function(resp) {
        if (resp.data.status === "success") {
          // turn off generall access while the doctor access is offed.
          if (access_type == "doc") {
            $('tr[name="record_' + file_id + '"]').find('label', '.checkbox-toggle').css("left", "18px");
            $('tr[name="record_' + file_id + '"]').find('.checkbox-toggle').css('background-color', "rgb(224, 0, 26)");
            form = new FormData()
            form.append("csrfmiddlewaretoken", csrftoken);
            form.append('file-id', file_id);
            form.append('toggle-action', 'off')
            form.append('access_type', "gen");
            axios
              .post(".", form)
              .then(function(resp) {})
              .catch(function(err) { console.log("err : ", err) });
          }
        }
      })
      .catch(function(err) { console.log("err : ", err) });
  }
});
// ----------------------------
