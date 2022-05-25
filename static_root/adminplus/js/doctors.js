// circle toggle button operations
$("div[name='account-status']").enhancedSwitch();
$("div[name='account-status']").each(function(index, el) {
  if ($(this).data("active") == "True") {
    $(el).enhancedSwitch('setFalse');
  } else {
    $(el).enhancedSwitch('setTrue');
  }
});

$("div[name='account-status']").click(function() {
  var selectedSwitch = $(this);
  selectedSwitch.enhancedSwitch('toggle');
  let user_id = $(this).data('doctor-id');
  // change to true
  if (selectedSwitch.enhancedSwitch('state')) {
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf_token);
    form.append('active_doctor', user_id);
    axios.post(".", form).then((response) => {}).catch((error) => {
      console.error(error);
    });
  } else {
    // changed to false
    Swal.fire({
      title: 'Suspend Account ?',
      text: "Doctor will not be able to login anymore.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, Continue!'
    }).then((result) => {
      if (result.isConfirmed) {
        let form = new FormData();
        form.append('csrfmiddlewaretoken', csrf_token);
        form.append('deactive_doctor', user_id);
        axios.post(".", form).then((response) => {
          Swal.fire(
            'Doctor Suspened!',
            'The doctor successfully suspend!',
            'success'
          )
        }).catch((error) => {
          console.error(error);
        });
      } else {
        // if not confirmed toggle again
        selectedSwitch.enhancedSwitch('toggle');
      }
    });
  }
});

// on delete
$("a[name='delete_doctor']").click(function(event) {
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
      let user_id = $(this).data("doctor-id");
      let form = new FormData();
      form.append('csrfmiddlewaretoken', csrf_token)
      form.append('delete_doctor', user_id);
      axios.post(".", form).then((response) => {
        Swal.fire(
          'Deleted!',
          'Doctor has been successfully deleted.',
          'success'
        );
        $(this).closest("tr").hide('slow');;
      }).catch((error) => {
        console.error(error);
      });
    }
  })
});


// dataTable
const rating4_star = `<i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i>`
const rating3_5_star = `<i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star-half-alt text-warning"></i>`
const rating3_star = `<i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star text-secondary"></i>`
const rating2_5_star = `<i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star-half-alt text-warning"></i><i class="fa fa-star text-secondary"></i>`
const rating2_star = `<i class="fa fa-star text-warning"></i><i class="fa fa-star text-warning"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i>`
const rating1_5_star = `<i class="fa fa-star text-warning"></i><i class="fa fa-star-half-alt text-warning"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i>`
const rating1_star = `<i class="fa fa-star text-warning"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i>`
const rating0_5_star = `<i class="fa fa-star-half-alt text-warning"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i>`
const rating0_star = `<i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i><i class="fa fa-star text-secondary"></i>`
const ratings = [rating0_star, rating0_5_star, rating1_star, rating1_5_star, rating2_star, rating2_5_star, rating3_star, rating3_5_star, rating4_star]

const r1 = rating0_star + " <i class='fa fa-arrow-right text-info'></i> " + rating1_star
const r2 = rating1_star + " <i class='fa fa-arrow-right text-info'></i> " + rating2_star
const r3 = rating2_star + " <i class='fa fa-arrow-right text-info'></i> " + rating3_star
const r4 = rating3_star + " <i class='fa fa-arrow-right text-info'></i> " + rating4_star


// making search fields
$('.cdatatable tfoot th span').each(function() {
  var title = $(this).text();
  $(this).html('<input type="text" class="form-control" placeholder="Search ' + title + '" />');
});

var table = $(".cdatatable").DataTable({
  "bFilter": false,
  "filter": true,
  "searching": true,
  // other customizations
  fixedColumns: true,
  language: {
    searchPanes: {
      clearMessage: 'Clear Filters',
      collapse: { 0: 'Search Filters', _: 'Active Filters (%d)' }
    },
  },
  buttons: [{
    extend: 'searchPanes',
  }],
  dom: 'Plfrtip',
  // dom: 'Bfrtlip',
  searchPanes: {
    viewTotal: true,
    show: true,
    layout: 'columns-2',
  },
  columnDefs: [{
      "visible": false,
      // "searchable": false,
      "searchable": true,
      targets: [2],
    },
    {
      orderable: false,
      searchPanes: {
        show: true,
        options: [{
            label: r1,
            value: function(rowData, rowIdx) {
              let data = $(rowData[1]).find('div[name="rating-stars"]').html();
              return data == ratings[0] || data == ratings[1] || data == ratings[2];
            }
          },
          {
            label: r2,
            value: function(rowData, rowIdx) {
              let data = $(rowData[1]).find('div[name="rating-stars"]').html();
              return data == ratings[3] || data == ratings[4];
            }
          },
          {
            label: r3,
            value: function(rowData, rowIdx) {
              let data = $(rowData[1]).find('div[name="rating-stars"]').html();
              return data == ratings[5] || data == ratings[6];
            }
          },
          {
            label: r4,
            value: function(rowData, rowIdx) {
              let data = $(rowData[1]).find('div[name="rating-stars"]').html();
              return data == ratings[7] || data == ratings[8];
            }
          },
        ],
      },
      targets: [1]
    },
    {
      searchPanes: {
        show: true,
        // combiner: "and",
      },
      targets: [2]
    },
  ],
});

// making search fields to work
table.columns().every(function() {
  var that = this;
  $('input', this.footer()).on('keyup change', function() {
    if (that.search() !== this.value) {
      that
        .search(this.value)
        .draw();
    }
  });
});



// styling dt-button
let btn_sp = $(".dt-button");
btn_sp.removeClass('dt-button');
btn_sp.addClass('btn btn-info');


console.log("now from here")
// graphs 
let endpoint = "/madmin/dashboard-graphs/"
console.log("now getting from the endpoint!")
axios.get(endpoint).then((response) => {
  console.log("response : ", response.data)
  console.log(" : ", response.data.doctors_by_province.user__address__city__name)
  console.log(" : ", response.data.doctors_by_province.user__address__city__name_count)
  console.log(response.data.doctors_by_province.male)
  console.log(response.data.doctors_by_province.female)

  let doctors_by_province_chart = new Chart($("#doctors_by_province_chart"), {
    type: 'horizontalBar',
    // type: 'bar',
    data: {
      labels: response.data.doctors_by_province.labels,
      datasets: [{
          label: '# Total',
          data: response.data.doctors_by_province.count,
          backgroundColor: "#ffd878",
          borderWidth: 1,
        },
        {
          label: '# Male',
          data: response.data.doctors_by_province.male,
          backgroundColor: 'rgba(75, 192, 192, 0.8)',
          borderWidth: 1,
        },
        {
          label: '# Female',
          data: response.data.doctors_by_province.female,
          backgroundColor: 'rgba(255, 99, 132, 0.8)',
          borderWidth: 1,
        },
        {
          label: '# Under Review',
          data: response.data.doctors_by_province.under_review,
          backgroundColor: 'grey',
          borderWidth: 1,
        },
      ]
    },    
    options: {
      // maintainAspectRatio: false,
      scales: {
        xAxes: [{
          ticks: {
            beginAtZero: true
          },
        }],
        // end of xAxes
        yAxes: [{}]
      },
      // end of yAxes

    }, // end of options
  });


}).catch((error) => {
  console.error(error);
}).finally(() => {
  // TODO
});