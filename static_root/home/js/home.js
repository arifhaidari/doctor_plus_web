let search_hints = $('div[name="search-hint"]')
// search_hints.css('display', 'none');
// $("input[name='searched-content']").keydown (function (e) {
// 	let value = $(this).val();
// 	let len = $(this).val().length;
//     // console.log(String.fromCharCode(e.which), $(this).val(), $(this).val().length);
//     console.log(len, value);
//     setTimeout(function() { console.log($('#search').val()) }, 1)
// });

function cleanData(str) {
  str = str.replaceAll("[", "")
  str = str.replaceAll("]", "")
  str = str.replaceAll(">", "")
  str = str.replaceAll("<", "")
  str = str.replaceAll("'", "")
  str = str.split(",");
  return str
}


let specialities = $("div[name='Specialities']")
let doctor_name = $("div[name='doc-items']")

let search_input = $("input[name='searched-content']")
search_input.on("input", function() {
  var dInput = this.value;
  // console.log(dInput, dInput.length);
  if (dInput.length >= 3) {
    search_hints.css('display', 'block');
    form = new FormData()
    form.append("csrfmiddlewaretoken", csrftoken);
    form.append('searched-content', dInput)
    $("div[name='sp-a']").html('')
    $("div[name='doc-items']").html('')
    
    axios
      .post(".", form)
      .then(function(resp) {
        console.log("resp : ", resp.data)
        for (data of resp.data.data){
	        $("div[name='doc-items']").append(`
	        	<div class="list-group-item tt-suggestion tt-selectable">
	                  <span>
	                    <div class="avatar">
	                      <img class="avatar-img rounded-circle d-inline" src="media/`+ data.user__avatar +`" alt="">
	                    </div>
	                  </span>
	                  <div class="text-dark text-left d-inline pl-2">
	                    <a href="#"><b>`+ data.user__full_name +`</b> 
	                    </a>
	                  </div>
	                </div>
	        `)
        }
        for (data of resp.data.speciality){
        	$("div[name='sp-a']").append(`
	        	<a href="#" class="list-group-item  tt-suggestion tt-selectable" name="sp-name">
					`+ data.name +`
				</a>
			`)
        }


      })
      .catch(function(err) {});
  } else {
    search_hints.css('display', 'none');
  }

});

$('div[name="sp-a"]').click(function() {
	search_hints.hide('slow');
	search_input.val($.trim($("a", this).html()))
  $("#search-form").submit();
});

$("div[name='doc-items']").click(function() {
  search_hints.hide('slow');
	search_input.val($.trim($("b", this).html()))
  $("#search-form").submit();
});


// sp categories clicked
function search_sp_cat (cat) {
  search_input.val(cat);
  $("form").submit();
}


// hide extra stars
$("div[name='rating-stars']").each( function(index, element) {
  // console.log("element : ", element, " element id ", $(element).prop('id'), " size : ", $(element).children().length)
  if (!$(element).prop('id')){
      $(element.remove())
  }
  while ($(element).children().length > 4) {
    $(element).children().last().remove();
  }
});
