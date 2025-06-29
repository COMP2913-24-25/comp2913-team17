// Assigning experts to authentication requests

$(document).ready(function() {
  // Update availability text when an expert is selected
  $('.expert-select').on('change', function() {
    const availability = $(this).find('option:selected').data('availability');
    $(this).closest('.d-flex.flex-column').find('.availability-text').text(availability);

    const expertise = $(this).find('option:selected').data('expertise');
    const expertiseText = $(this).closest('.d-flex').find('.expertise-text');

    // Update the colouring of the pill
    if (expertise === 'Expert') {
      expertiseText.html('<i class="fas fa-check"></i> ' + expertise);
      expertiseText.removeClass('bg-danger');
      expertiseText.addClass('bg-success');
    } else {
      expertiseText.html('<i class="fas fa-times"></i> ' + expertise);
      expertiseText.removeClass('bg-success');
      expertiseText.addClass('bg-danger');
    }
  });
  
  // Trigger change event on page load to set initial availability text
  $('.expert-select').trigger('change');
  
  // Assign an expert to an authentication request (Manual Assignment)
  $('.assign-expert-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const requestId = row.data('request-id');
    const expert = row.find('.expert-select').val();

    // Change assign button to spinner
    $(this).html(`
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 
      Assigning...
    `);
    $(this).prop('disabled', true);

    try {
      const response = await csrfFetch(`/dashboard/api/assign-expert/${requestId}`, {
        method: 'POST',
        body: JSON.stringify({ expert: parseInt(expert) })
      });
      const data = await response.json();
      
      if (response.ok) {
        // Show success message
        alert('Expert assigned successfully');

        // Remove the row with animation
        row.fadeOut(300, function() {
          $(this).remove();
          checkEmptyTable();
        });
      } else {
        // Show error and do not remove the row
        alert(data.error || "Error assigning expert.");

        // Reset the button
        $(this).html(`<i class="fas fa-user-check me-1"></i> Assign`);
        $(this).prop('disabled', false);
      }
    } catch (error) {
      console.log('Error:', error);
      alert("Error assigning expert.");

      // Reset the button
      $(this).html(`<i class="fas fa-user-check me-1"></i> Assign`);
      $(this).prop('disabled', false);
    }
  });

  $('.auto-assign-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const requestId = row.data('request-id');
    const expertId = $(this).data('expert-id');

    // Change Auto-Assign button to spinner
    $(this).html(`
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 
      Assigning...
    `);
    $(this).prop('disabled', true);

    try {
      const response = await csrfFetch(`/dashboard/api/auto-assign-expert/${requestId}`, {
        method: 'POST',
        body: JSON.stringify({'recommendation': parseInt(expertId)})
      });
      const data = await response.json();
      
      if (response.ok) {
        // Show success message
        alert('Expert auto-assigned successfully');
        window.location.reload();
      } else {
        // Show error and do not remove the row
        alert(data.error || "Error auto-assigning expert.");

        // Reset the button
        $(this).html(`<i class="fas fa-user-check me-1"></i> Auto-Assign`);
        $(this).prop('disabled', false);
      }
    } catch (error) {
      console.log('Error:', error);
      alert("Error auto-assigning expert.");

      // Reset the button
      $(this).html(`<i class="fas fa-user-check me-1"></i> Auto-Assign`);
      $(this).prop('disabled', false);
    }
  });

  $('#select-all-requests').on('change', function() {
    $('.request-checkbox').prop('checked', this.checked);
    $('#mobile-select-all-requests').prop('checked', this.checked);
  });

  $('#mobile-select-all-requests').on('change', function() {
    $('.request-checkbox').prop('checked', this.checked);
    $('#select-all-requests').prop('checked', this.checked);
  });

  $('.bulk-auto-assign-btn').on('click', async function() {
    const selectedRows = $('.request-checkbox:checked').closest('tr');
    if (selectedRows.length === 0) {
      showErrorBanner('Please select at least one request to auto-assign.');
      return;
    }

    // Change button to spinner
    $(this).html(`
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 
      Assigning...
    `);
    $(this).prop('disabled', true);

    const requestIds = selectedRows.map(function() {
      return $(this).data('request-id');
    }).get();

    try {
      const response = await csrfFetch('/dashboard/api/bulk-auto-assign-experts', {
        method: 'POST',
        body: JSON.stringify({ request_ids: requestIds })
      });
      const data = await response.json();

      if (response.ok) {
        // Show success message
        if (data.assignments.length == 0) {
          alert('No available experts for the selected requests.');
          window.location.reload();
          return;
        }
        alert('Bulk auto-assignment successful: ' + data.assignments.length + ' requests assigned.');
        window.location.reload();
      } else {
        // Show error and do not remove rows
        alert(data.error || "Error during bulk auto-assignment.");

        // Reset the button
        $(this).html('Bulk Auto-Assign');
        $(this).prop('disabled', false);
      }
    } catch (error) {
      console.log('Error:', error);
      alert("Error during bulk auto-assignment.");

      // Reset the button
      $(this).html('Bulk Auto-Assign');
      $(this).prop('disabled', false);
    }
  });

  function checkEmptyTable() {
    if ($('#auth-requests-card table tbody tr').length === 0) {
      $('#auth-requests-card').replaceWith(`
        <div class="empty-state">
          <i class="fas fa-clipboard-check"></i>
          <p class="empty-state-text">No pending authentication requests at this time.</p>
        </div>
      `);
    }
  }
  
  function showErrorBanner(message) {
    // Remove any existing error banners
    $('.error-banner').remove();
    
    // Create the banner
    const banner = $(`
      <div class="error-banner alert alert-danger alert-dismissible fade show" role="alert">
        <i class="fas fa-exclamation-circle me-2"></i>
        <strong>Error!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `);
    
    // Add the banner to the top of the requests tab content
    $('#requests').prepend(banner);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      banner.alert('close');
    }, 5000);
  }
});