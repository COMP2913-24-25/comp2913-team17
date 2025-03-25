// Management Charts for the Dashboard

document.addEventListener('DOMContentLoaded', function () {
  const ctx = document.getElementById('revenueChart');
  if (ctx) {
    // Get all data from data attributes
    const data = {
      week: {
        projected: {
          labels: JSON.parse(ctx.dataset.weekProjectedLabels || '[]'),
          values: JSON.parse(ctx.dataset.weekProjectedValues || '[]')
        },
        paid: {
          labels: JSON.parse(ctx.dataset.weekPaidLabels || '[]'),
          values: JSON.parse(ctx.dataset.weekPaidValues || '[]')
        }
      },
      month: {
        projected: {
          labels: JSON.parse(ctx.dataset.monthProjectedLabels || '[]'),
          values: JSON.parse(ctx.dataset.monthProjectedValues || '[]')
        },
        paid: {
          labels: JSON.parse(ctx.dataset.monthPaidLabels || '[]'),
          values: JSON.parse(ctx.dataset.monthPaidValues || '[]')
        }
      },
      six_months: {
        projected: {
          labels: JSON.parse(ctx.dataset.sixMonthsProjectedLabels || '[]'),
          values: JSON.parse(ctx.dataset.sixMonthsProjectedValues || '[]')
        },
        paid: {
          labels: JSON.parse(ctx.dataset.sixMonthsPaidLabels || '[]'),
          values: JSON.parse(ctx.dataset.sixMonthsPaidValues || '[]')
        }
      }
    };

    // Initialise chart with 6 months projected revenue as default
    const revenueChart = new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
        labels: data.six_months.projected.labels,
        datasets: [{
          label: 'Projected Revenue (£)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
          data: data.six_months.projected.values
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Revenue (£)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Time'
            }
          }
        }
      }
    });

    // Function to update chart
    function updateChart(period, revenueType) {
      revenueChart.data.labels = data[period][revenueType].labels;
      revenueChart.data.datasets[0].data = data[period][revenueType].values;
      revenueChart.data.datasets[0].label = revenueType === 'projected' ? 'Projected Revenue (£)' : 'Paid Revenue (£)';
      revenueChart.update();
    }

    // Time period toggle
    const timeToggles = document.querySelectorAll('.time-toggle');
    let currentPeriod = 'six_months';
    let currentRevenueType = 'projected';

    timeToggles.forEach(toggle => {
      toggle.addEventListener('change', function () {
        if (this.checked) {
          currentPeriod = this.value;
          updateChart(currentPeriod, currentRevenueType);
        }
      });
    });

    // Revenue type toggle
    const revenueToggles = document.querySelectorAll('.revenue-toggle');
    revenueToggles.forEach(toggle => {
      toggle.addEventListener('change', function () {
        if (this.checked) {
          currentRevenueType = this.value;
          updateChart(currentPeriod, currentRevenueType);
        }
      });
    });
  }
});