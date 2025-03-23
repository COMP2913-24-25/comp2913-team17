// Management Charts for the Dashboard

document.addEventListener('DOMContentLoaded', function () {
  const ctx = document.getElementById('revenueChart');
  if (ctx) {
    const revenueChart = new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Revenue (£)',
          backgroundColor: 'rgba(234, 217, 184, 0.2)', // Beige fill
          borderColor: '#EAD9B8', // Beige line
          borderWidth: 1,
          data: []
        }]
      },
      options: {
        animation: {
          duration: 1000, // Animation duration in milliseconds (1 second)
          easing: 'easeInOutQuad' // Smooth easing function for a natural feel
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Revenue (£)' }
          },
          x: {
            title: { display: true, text: 'Time' },
            ticks: {
              autoSkip: true, // Automatically skip labels to prevent overlap
              maxTicksLimit: 5, // Limit the number of ticks to 5
              callback: function(value, index, ticks) {
                const label = this.getLabelForValue(value);
                const period = $('.btn-group [data-period].active').data('period');
                if (period === '1w') {
                  // For "1 Week", show only the day
                  return label.split('-')[2]; // Extracts the day from "YYYY-MM-DD"
                } else if (period === '1m') {
                  // For "1 Month", show only the week number
                  return label.split('-')[1]; // Extracts the week from "YYYY-WW"
                }
                // For "6 Months", show the month
                return label.split('-')[1]; // Extracts the month from "YYYY-MM"
              }
            }
          }
        },
        responsive: true,
        maintainAspectRatio: false // Allow the chart to fill the container
      }
    });

    function updateChart() {
      const revenueType = $('.btn-group [data-revenue-type].active').data('revenue-type');
      const period = $('.btn-group [data-period].active').data('period');
      fetch(`/dashboard/api/revenue?type=${revenueType}&period=${period}`)
        .then(response => response.json())
        .then(data => {
          revenueChart.data.labels = data.labels;
          revenueChart.data.datasets[0].data = data.data;
          revenueChart.update();
        })
        .catch(error => {
          console.error('Error fetching revenue data:', error);
          alert('Failed to load revenue data.');
        });
    }

    $('.btn-group [data-revenue-type]').on('click', function() {
      $('.btn-group [data-revenue-type]').removeClass('active');
      $(this).addClass('active');
      updateChart();
    });

    $('.btn-group [data-period]').on('click', function() {
      $('.btn-group [data-period]').removeClass('active');
      $(this).addClass('active');
      updateChart();
    });

    updateChart();
  }
});