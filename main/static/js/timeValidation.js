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
  
      if (startTime && startTime < minTime) {
        row.find('.start-input').addClass('is-invalid')
            .after('<div class="time-error text-danger">Start time must be at or after 08:00.</div>');
      }
      if (startTime && startTime > maxTime) {
        row.find('.start-input').addClass('is-invalid')
            .after('<div class="time-error text-danger">Start time must be at or before 20:00.</div>');
      }
      if (endTime && endTime > maxTime) {
        row.find('.end-input').addClass('is-invalid')
            .after('<div class="time-error text-danger">End time must be at or before 20:00.</div>');
      }
      if (endTime && endTime < minTime) {
        row.find('.end-input').addClass('is-invalid')
            .after('<div class="time-error text-danger">End time must be at or after 08:00.</div>');
      }
      if (startTime && endTime && startTime >= endTime) {
        row.find('.end-input').addClass('is-invalid')
            .after('<div class="time-error text-danger">End time must be later than start time.</div>');
      }
    });
    
    // Listen for changes on the status select field
    $('.status-select').on('change', function() {
      const row = $(this).closest('tr');
      const status = $(this).val();
      // If the status is set to unavailable, disable & grey out only the time inputs
      if (status === 'unavailable') {
        row.find('.start-input, .end-input')
            .prop('disabled', true)
            .addClass('disabled-input')
      } else {
        row.find('.start-input, .end-input')
            .prop('disabled', false)
            .removeClass('disabled-input');
      }
    });

    // Handler for "Mark Whole Week as Unavailable" button
    $('#mark-week-unavailable').on('click', function(){
        // For each enabled status-select, set its value to "unavailable" and trigger change
        $('.status-select:not(:disabled)').each(function(){
            $(this).val('unavailable').trigger('change');
        });
    });
});
