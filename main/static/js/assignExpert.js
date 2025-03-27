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
  
  function showSuccessBanner(message) {
    // Remove any existing banners
    $('.success-banner').remove();
    
    // Create the banner
    const banner = $(`
      <div class="success-banner alert alert-success alert-dismissible fade show" role="alert">
        <i class="fas fa-check-circle me-2"></i>
        <strong>Success!</strong> ${message}
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
  
  function showAssignConfirmation(type, options) {
    if ($('#assignConfirmationModal').length > 0) {
      $('#assignConfirmationModal').remove();
    }
    
    let title, body, confirmBtnText;
    
    if (type === 'manual') {
      title = 'Confirm Expert Assignment';
      body = `
        <p>Are you sure you want to assign <strong>${options.expertName}</strong> to this authentication request?</p>
        <div class="d-flex align-items-center mt-2 mb-2">
          <span class="me-2">Expertise:</span>
          <span class="badge ${options.expertise === 'Expert' ? 'bg-success' : 'bg-danger'} me-3">
            <i class="fas ${options.expertise === 'Expert' ? 'fa-check' : 'fa-times'}"></i> ${options.expertise}
          </span>
        </div>
        <div class="d-flex align-items-center">
          <span class="me-2">Availability:</span>
          <span class="badge ${options.availability.includes('Available') ? 'bg-success' : 'bg-warning'}">
            ${options.availability}
          </span>
        </div>
      `;
      confirmBtnText = 'Yes, Assign Expert';
    } else if (type === 'auto') {
      title = 'Confirm Auto-Assignment';
      body = `
        <p>Are you sure you want to auto-assign the recommended expert to this authentication request?</p>
        <p>The system will select the most suitable expert based on expertise and availability.</p>
      `;
      confirmBtnText = 'Yes, Auto-Assign';
    } else if (type === 'bulk') {
      title = 'Confirm Bulk Auto-Assignment';
      body = `
        <p>Are you sure you want to auto-assign experts to <strong>${options.count}</strong> selected requests?</p>
        <p>The system will select the most suitable experts based on expertise and availability.</p>
      `;
      confirmBtnText = 'Yes, Bulk Auto-Assign';
    }
    
    $('body').append(`
      <div class="modal fade" id="assignConfirmationModal" tabindex="-1" aria-labelledby="assignConfirmationModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="assignConfirmationModalLabel">${title}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              ${body}
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" id="confirm-assign-btn">${confirmBtnText}</button>
            </div>
          </div>
        </div>
      </div>
    `);
    
    const assignModal = new bootstrap.Modal(document.getElementById('assignConfirmationModal'));
    assignModal.show();

    $('#confirm-assign-btn').off('click').on('click', function() {
      assignModal.hide();
      
      if (type === 'manual') {
        performManualAssignment(options.requestId, options.expert, options.row);
      } else if (type === 'auto') {
        performAutoAssignment(options.requestId, options.row);
      } else if (type === 'bulk') {
        performBulkAutoAssignment(options.requestIds, options.selectedRows);
      }
    });
  }

  async function performManualAssignment(requestId, expert, row) {
    try {
      const response = await csrfFetch(`/dashboard/api/assign-expert/${requestId}`, {
        method: 'POST',
        body: JSON.stringify({ expert: parseInt(expert) })
      });
      const data = await response.json();
      
      if (response.ok) {
        // Show success banner instead of alert
        showSuccessBanner('Expert assigned successfully');

        // Remove the row with animation
        row.fadeOut(300, function() {
          $(this).remove();
          checkEmptyTable();
        });
      } else {
        // Show error banner instead of alert
        showErrorBanner(data.error || "Error assigning expert.");
      }
    } catch (error) {
      console.log('Error:', error);
      showErrorBanner("Error assigning expert.");
    }
  }
  
  // Perform auto assignment after confirmation
  async function performAutoAssignment(requestId, row) {
    try {
      const response = await csrfFetch(`/dashboard/api/auto-assign-expert/${requestId}`, {
        method: 'POST',
        body: JSON.stringify({}) // No body needed, but keeping it consistent
      });
      const data = await response.json();
      
      if (response.ok) {
        // Show success banner instead of alert
        showSuccessBanner('Expert auto-assigned successfully');

        // Remove the row with animation
        row.fadeOut(300, function() {
          $(this).remove();
          checkEmptyTable();
        });
      } else {
        // Show error banner instead of alert
        showErrorBanner(data.error || "Error auto-assigning expert.");
      }
    } catch (error) {
      console.log('Error:', error);
      showErrorBanner("Error auto-assigning expert.");
    }
  }
  
  // Perform bulk auto assignment after confirmation
  async function performBulkAutoAssignment(requestIds, selectedRows) {
    try {
      const response = await csrfFetch('/dashboard/api/bulk-auto-assign-experts', {
        method: 'POST',
        body: JSON.stringify({ request_ids: requestIds })
      });
      const data = await response.json();

      if (response.ok) {
        // Show success banner instead of alert
        showSuccessBanner('Bulk auto-assignment successful: ' + data.assignments.length + ' requests assigned.');

        // Remove assigned rows with animation
        selectedRows.fadeOut(300, function() {
          $(this).remove();
          checkEmptyTable();
        });
      } else {
        // Show error banner instead of alert
        showErrorBanner(data.error || "Error during bulk auto-assignment.");
      }
    } catch (error) {
      console.log('Error:', error);
      showErrorBanner("Error during bulk auto-assignment.");
    }
  }
});