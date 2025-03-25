// Management Charts for the Dashboard

document.addEventListener('DOMContentLoaded', function () {
  const ctx = document.getElementById('revenueChart');
  if (ctx) {
    // Get all data from data attributes
    const data = {
      week: {
        labels: JSON.parse(ctx.dataset.weekLabels || '[]'),
        values: JSON.parse(ctx.dataset.weekValues || '[]')
      },
      month: {
        labels: JSON.parse(ctx.dataset.monthLabels || '[]'),
        values: JSON.parse(ctx.dataset.monthValues || '[]')
      },
      six_months: {
        labels: JSON.parse(ctx.dataset.sixMonthsLabels || '[]'),
        values: JSON.parse(ctx.dataset.sixMonthsValues || '[]')
      }
    };

    // Initialize chart with 6 months as default
    const revenueChart = new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
        labels: data.six_months.labels,
        datasets: [{
          label: 'Revenue (£, Paid Auctions)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
          data: data.six_months.values
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

    // Toggle functionality
    const toggleButtons = document.querySelectorAll('.time-toggle');
    toggleButtons.forEach(button => {
      button.addEventListener('click', function () {
        const period = this.dataset.period;

        // Update chart data
        revenueChart.data.labels = data[period].labels;
        revenueChart.data.datasets[0].data = data[period].values;
        revenueChart.update();

        // Update active button
        toggleButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }
});