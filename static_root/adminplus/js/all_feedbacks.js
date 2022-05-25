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




// datatable
$('.cdatatable').DataTable({
  "bFilter": false,
  "filter": true,
  "searching": true,
  // added after this
  searchPanes: {
    viewTotal: true,
    columns: [1, 5, 4]
  },
  dom: 'Plfrtip',
  columnDefs: [{
      "visible": false,
      "searchable": true,
      targets: [4, 5],
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
        ]
      },
      targets: [1]
    },
    {
      searchPanes: {
        show: true,
        options: [{
            label: 'Male',
            value: function(rowData, rowIdx) {
              return rowData[5] == "Male";
            }
          },
          {
            label: 'Female',
            value: function(rowData, rowIdx) {
              return rowData[5] == "Female";
            }
          },
        ]
      },
      targets: [5]
    },
    {
      searchPanes: {
        show: true,
        // [
        //   {
        //     label: 'Not London',
        //     value: function(rowData, rowIdx) {
        //       return rowData[3] !== 'London';
        //     }
        //   }
        // ],
        // combiner: 'and'
      },
      targets: [4]
    }
  ],
  select: {
    style: 'os',
    selector: 'td:first-child'
  },
  order: [
    [1, 'asc']
  ]
});


$(".dataTables_length").addClass('mt-5 mb-n5')