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
          backgroundColor: 'rgba(0, 123, 255, 0.2)', // Default to blue fill (All Revenue)
          borderColor: '#007bff', // Default to blue line
          borderWidth: 2,
          data: [],
          fill: true
        }]
      },
      options: {
        animation: {
          duration: 1000,
          easing: 'easeInOutQuad'
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Revenue (£)' }
          },
          x: {
            title: { display: true, text: 'Time' },
            ticks: {
              autoSkip: true,
              maxTicksLimit: 5,
              callback: function(value, index, ticks) {
                const label = this.getLabelForValue(value);
                const period = $('.btn-group [data-period].active').data('period');
                if (period === '1w') {
                  return label.split('-')[2]; // Day
                } else if (period === '1m') {
                  return label.split('-')[1]; // Week
                }
                return label.split('-')[1]; // Month
              }
            }
          }
        },
        responsive: true,
        maintainAspectRatio: false
      }
    });

    function updateChart() {
      const revenueType = $('.btn-group [data-revenue-type].active').data('revenue-type');
      const period = $('.btn-group [data-period].active').data('period');

      // Update chart colors based on revenue type
      if (revenueType === 'all') {
        revenueChart.data.datasets[0].label = 'All Revenue (£)';
        revenueChart.data.datasets[0].backgroundColor = 'rgba(0, 123, 255, 0.2)'; // Blue fill
        revenueChart.data.datasets[0].borderColor = '#007bff'; // Blue line
      } else if (revenueType === 'paid') {
        revenueChart.data.datasets[0].label = 'Paid Revenue (£)';
        revenueChart.data.datasets[0].backgroundColor = 'rgba(255, 127, 14, 0.2)'; // Orange fill
        revenueChart.data.datasets[0].borderColor = '#ff7f0e'; // Orange line
      }

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

    // Initial chart load
    updateChart();
  }
});