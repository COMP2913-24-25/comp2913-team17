document.addEventListener('DOMContentLoaded', function() {
    // Real-time validation for time fields
    $('.start-input, .end-input').on('input', function() {
      const row = $(this).closest('tr');
      const startTime = row.find('.start-input').val();
      const endTime = row.find('.end-input').val();
      const minTime = "08:00";
      const maxTime = "20:00";
  
      // Remove any existing error messages and styling
      row.find('.time-error').remove();
      row.find('.start-input, .end-input').removeClass('is-invalid');
  
      // Check that the start time is not before 08:00 AM
      if (startTime && startTime < minTime) {
        row.find('.start-input').addClass('is-invalid');
        row.find('.start-input').after('<div class="time-error text-danger">Start time must be at or after 08:00.</div>');
      }
      
      // Check that the start time is not after 08:00 PM
      if (startTime && startTime > maxTime) {
        row.find('.start-input').addClass('is-invalid');
        row.find('.start-input').after('<div class="time-error text-danger">Start time must be at or before 20:00.</div>');
      }
      
      // Check that the end time is not after 08:00 PM
      if (endTime && endTime > maxTime) {
        row.find('.end-input').addClass('is-invalid');
        row.find('.end-input').after('<div class="time-error text-danger">End time must be at or before 20:00.</div>');
      }
      
      // Check that the end time is not before 08:00 AM
      if (endTime && endTime < minTime) {
        row.find('.end-input').addClass('is-invalid');
        row.find('.end-input').after('<div class="time-error text-danger">End time must be at or after 08:00.</div>');
      }
  
      // Check that the end time is later than the start time
      if (startTime && endTime && startTime >= endTime) {
        row.find('.end-input').addClass('is-invalid');
        row.find('.end-input').after('<div class="time-error text-danger">End time must be later than start time.</div>');
      }
    });
  
    // Listen for changes on the status select field
    $('.status-select').on('change', function() {
      const row = $(this).closest('tr');
      if ($(this).val() === 'unavailable') {
        // Disable the time inputs and add a disabled style
        row.find('.start-input, .end-input').prop('disabled', true).addClass('bg-secondary text-white');
      } else {
        // Re-enable the time inputs and remove the disabled style
        row.find('.start-input, .end-input').prop('disabled', false).removeClass('bg-secondary text-white');
      }
    });
  });
  