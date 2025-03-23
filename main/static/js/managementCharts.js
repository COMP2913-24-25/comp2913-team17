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
        animation: false, // Disable animations for better performance
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Revenue (£)' }
          },
          x: {
            title: { display: true, text: 'Time' }
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