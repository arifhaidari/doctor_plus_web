jQuery(document).ready(function($) {
  // console.log("PATIENT.JS")
  // var file_id = $('#file-id')

  var checkbox = $(".checkbox-toggle")
  var tab_medical_record = $('#medicalrecord')
  tab_medical_record.click();

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
      // $("input", this).prop("checked", true)
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
          // console.log("sent off request ", access_type)
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

  var editFormData = $('form[name="editForm"]')
  editFormData.submit(function(event) {
    event.preventDefault();
    form = $(this).serialize()
    axios
      .post(".", form)
      .then(function(resp) {
        if (resp.data.status === "success") {
          $("button[name='close-edit']").click();
          $('td[name="record_title_' + resp.data.updated_id + '"]').text(resp.data.title);
        }
      })
      .catch(function(err) { console.log("err : ", err) });
  });

  var deleteFormData = $('form[name="deleteForm"]')
  deleteFormData.submit(function(event) {
    event.preventDefault();
    form = $(this).serialize()
    axios
      .post(".", form)
      .then(function(resp) {
        // console.log("Submission cancelled Response Form ")
        if (resp.data.status === "success") {
          $("button[name='close-delete']").click();
          $("tr[name='record_" + resp.data.deleted_id + "']").remove();
        }
      })
      .catch(function(err) { console.log("err : ", err) });
  });


  // sorting options
  $('th').click(function() {
    var table = $(this).parents('table').eq(0)
    var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
    this.asc = !this.asc
    if (!this.asc) { rows = rows.reverse() }
    for (var i = 0; i < rows.length; i++) { table.append(rows[i]) }
  })

  function comparer(index) {
    return function(a, b) {
      var valA = getCellValue(a, index),
        valB = getCellValue(b, index)
      return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
    }
  }

  function getCellValue(row, index) { return $(row).children('td').eq(index).text() }



  // end reday.function() 
});