document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[type="time"]').forEach(input => {
      input.addEventListener('change', function() {
        const minTime = "08:00";
        const maxTime = "20:00";
        if (this.value < minTime) {
          this.value = minTime;
        } else if (this.value > maxTime) {
          this.value = maxTime;
        }
      });
    });
  });
  