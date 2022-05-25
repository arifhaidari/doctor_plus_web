console.log("here is our home search!")

function isLetter(c) {
  if (c.trim()) {
    return true
  }
  return false
}


let male_checkbutton = $('#male_checkbox')
let female_checkbutton = $('#female_checkbox')

male_checkbutton.click(function() {
  is_checked = $(this).prop("checked")
  for (i of $('div[name="doctor-item"]')) {
    // console.log(i)
    // console.log($(i).find('input[name="gender"]').val())
    if ($(i).find('input[name="gender"]').val() == "MALE") {
      $(i).toggle('slow')
    }
  }
});

female_checkbutton.click(function() {
  is_checked = $(this).prop("checked")
  for (i of $('div[name="doctor-item"]')) {
    if ($(i).find('input[name="gender"]').val() == "FEMALE") {
      $(i).toggle('slow')
    }
  }
});

let sp_cat_close = $('div[name="speciality"]')
sp_cat_close.find('span[name="close-sp-cat"]').click(function() {
  $(this).parent().parent().parent('div[name="speciality"]').parent().find('input[name="select_specialist"]').prop('checked', false);
  $(this).parent().parent().parent('div[name="speciality"]').parent().hide('slow/400/fast');
  // console.log("gene ",s)

  for (i of $('div[name="doctor-item"]')) {
    if (
      $(i).find('input[name="speciality"]').val()
      .includes($(this).parent().parent().parent('div[name="speciality"]').find('input[name="sepecility-cat"]').val())
    ) {
      let removed_cat = $(this).parent().parent().parent('div[name="speciality"]').find('input[name="sepecility-cat"]').val()
      let cat_list = $(i).find('input[name="speciality"]').val()
      console.log(" that , ", cat_list)
      cat_list = cat_list.replaceAll("'", '');
      cat_list = cat_list.replaceAll(",", '');
      cat_list = cat_list.replaceAll("[", '');
      cat_list = cat_list.replaceAll("]", '');
      cat_list = cat_list.replace(removed_cat, "");
      $(i).find('input[name="speciality"]').val(cat_list)
      let has_other_related_speciality = isLetter($(i).find('input[name="speciality"]').val());
      // console.log("yess after that ", cat_list)
      // console.log("has any other related speciality : ", has_other_related_speciality)
      if (!has_other_related_speciality){
      	$(i).hide('slow');
      }
    }
  }
});


let sp_checkboxes = $('input[name="select_specialist"]')
sp_checkboxes.click(function(){
	// is_checked = $(this).prop('checked')
  for (i of $('div[name="doctor-item"]')) {
    // if ($(i).find('input[name="gender"]').val() == "FEMALE") {
    //   $(i).toggle('slow')
    // }
    speciality_items = $(i).find('input[name="speciality-item"]').val()
    removed_item = $(this).parent().parent().find('input[name="speciality-item"]').val()
    console.log(speciality_items)
    console.log(removed_item)
    if(speciality_items.includes(removed_item)){
    	console.log("before : ", speciality_items)
    	speciality_items = speciality_items.replaceAll("'", '');
      speciality_items = speciality_items.replaceAll(",", '');
      speciality_items = speciality_items.replaceAll("[", '');
      speciality_items = speciality_items.replaceAll("]", '');

      speciality_items = speciality_items.replace(removed_item, "");
      $(i).find('input[name="speciality-item"]').val(speciality_items)
    	console.log("after : ", speciality_items)
    	
    	let has_other_related_speciality = isLetter(speciality_items);
    	console.log(has_other_related_speciality)
    	if (!has_other_related_speciality){
    		$(i).toggle('slow')
    	}
    	$(i).find('input[name="speciality-item"]').val(speciality_items+removed_item)
    }

  }
});