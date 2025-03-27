// Management Charts for the Dashboard

document.addEventListener('DOMContentLoaded', function () {
  const ctx = document.getElementById('revenueChart');
  if (ctx) {
    const style = getComputedStyle(document.documentElement);
    const primaryColor = style.getPropertyValue('--primary-color') || '#000';
    const accentColor = style.getPropertyValue('--accent-color') || '#ff9d00';
    const secondaryColor = style.getPropertyValue('--secondary-color') || '#fff';
    
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

    // Set responsive options for the chart
    ctx.style.maxHeight = '400px';
    ctx.parentElement.style.position = 'relative';
    
    // Initialise chart with 6 months projected revenue as default
    const revenueChart = new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
        labels: data.six_months.projected.labels,
        datasets: [{
          label: 'Projected Revenue (£)',
          backgroundColor: `${accentColor}`,
          borderColor: accentColor,
          borderWidth: 2,
          pointBackgroundColor: accentColor,
          pointBorderColor: secondaryColor,
          pointRadius: 4,
          pointHoverRadius: 6,
          data: data.six_months.projected.values,
          tension: 0.2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            align: 'start',
            labels: {
              boxWidth: 15,
              usePointStyle: true,
              pointStyle: 'circle',
              font: {
                family: "'Inter', sans-serif",
                size: function() {
                  return window.innerWidth < 768 ? 10 : 12;
                }
              }
            }
          },
          tooltip: {
            backgroundColor: primaryColor,
            titleFont: {
              family: "monospace, sans-serif",
              size: 14,
              weight: 'bold'
            },
            bodyFont: {
              family: "'Inter', sans-serif",
              size: 13
            },
            padding: 10,
            cornerRadius: 0,
            displayColors: false,
            callbacks: {
              label: function(context) {
                return `£${context.parsed.y.toFixed(2)}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: `${primaryColor}`,
              drawBorder: false
            },
            ticks: {
              font: {
                family: "monospace, sans-serif",
                size: function() {
                  return window.innerWidth < 768 ? 9 : 11;
                }
              },
              callback: function(value) {
                return '£' + value;
              }
            },
            title: {
              display: true,
              text: 'Revenue (£)',
              font: {
                family: "monospace, sans-serif",
                size: function() {
                  return window.innerWidth < 768 ? 10 : 12;
                },
                weight: 'bold'
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45,
              font: {
                family: "monospace, sans-serif",
                size: function() {
                  return window.innerWidth < 768 ? 8 : 10;
                }
              }
            },
            title: {
              display: true,
              text: 'Time',
              font: {
                family: "monospace, sans-serif",
                size: function() {
                  return window.innerWidth < 768 ? 10 : 12;
                },
                weight: 'bold'
              }
            }
          }
        }
      }
    });

    // Function to update chart
    function updateChart(period, revenueType) {
      revenueChart.data.labels = data[period][revenueType].labels;
      revenueChart.data.datasets[0].data = data[period][revenueType].values;
      
      if (revenueType === 'projected') {
        revenueChart.data.datasets[0].label = 'Projected Revenue (£)';
        revenueChart.data.datasets[0].borderColor = accentColor;
        revenueChart.data.datasets[0].backgroundColor = `${accentColor}33`;
        revenueChart.data.datasets[0].pointBackgroundColor = accentColor;
      } else {
        revenueChart.data.datasets[0].label = 'Paid Revenue (£)';
        revenueChart.data.datasets[0].borderColor = '#28a745';
        revenueChart.data.datasets[0].backgroundColor = '#28a74533';
        revenueChart.data.datasets[0].pointBackgroundColor = '#28a745';
      }
      
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