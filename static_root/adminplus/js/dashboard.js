let endpoint = "/madmin/dashboard-graphs/"

axios.get(endpoint).then((response) => {
  console.log("response : ", response.data)
  console.log(" : ", response.data.doctors_by_province.user__address__city__name)
  console.log(" : ", response.data.doctors_by_province.user__address__city__name_count)


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

  let patients_by_province_chart = new Chart($("#patients_by_province_chart"), {
    // type: 'polarArea',
    type: 'horizontalBar',
    data: {
      labels: response.data.patients_by_province.labels,
      datasets: [{
          label: '# Total',
          data: response.data.patients_by_province.count,
          backgroundColor: [
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 109, 184, 0.8)',
            'rgba(255, 252, 64, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(255, 159, 164, 0.8)',
            'rgba(255, 159, 264, 0.8)',
            'rgba(255, 259, 64, 0.8)',
          ],
          borderWidth: 1,
        },
        {
          label: '# Male',
          data: response.data.patients_by_province.male,
          backgroundColor: 'rgba(75, 192, 192, 0.8)',
          borderWidth: 1,
        },
        {
          label: '# Female',
          data: response.data.patients_by_province.female,
          backgroundColor: 'rgba(255, 99, 132, 0.8)',
          borderWidth: 1,
        },
      ]
    },
  });


  let appointments_by_province_chart = new Chart($("#appointments_by_province_chart"), {
    // type: 'doughnut',
    type: 'horizontalBar',
    data: {
      labels: response.data.compeleted_apps_by_province.labels,
      datasets: [{
          label: '# Total',
          data: response.data.compeleted_apps_by_province.count,
          backgroundColor: [
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 109, 184, 0.8)',
            'rgba(255, 252, 64, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(255, 159, 164, 0.8)',
            'rgba(255, 159, 264, 0.8)',
            'rgba(255, 259, 64, 0.8)',
          ],
          borderWidth: 1,
        },
        {
          label: '# Booked',
          data: response.data.compeleted_apps_by_province.booked,
          backgroundColor: 'lightpink',
          borderWidth: 1,
        },
        {
          label: '# Compeleted',
          data: response.data.compeleted_apps_by_province.completed,
          backgroundColor: 'lightgreen',
          borderWidth: 1,
        },
        {
          label: '# Pending',
          data: response.data.compeleted_apps_by_province.pending,
          backgroundColor: 'grey',
          borderWidth: 1,
        },

      ]
    },
  });



}).catch((error) => {
  console.error(error);
}).finally(() => {
  // TODO
});