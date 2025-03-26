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
  $('.assign-expert-btn').on('click', function() {
    const row = $(this).closest('tr');
    const requestId = row.data('request-id');
    const expertSelect = row.find('.expert-select');
    const expert = expertSelect.val();
    const expertName = expertSelect.find('option:selected').text();
    const expertise = expertSelect.find('option:selected').data('expertise');
    const availability = expertSelect.find('option:selected').data('availability');
    
    showAssignConfirmation('manual', {
      requestId, 
      expert, 
      expertName, 
      expertise, 
      availability, 
      row
    });
  });

  $('.auto-assign-btn').on('click', function() {
    const row = $(this).closest('tr');
    const requestId = row.data('request-id');
    
    showAssignConfirmation('auto', {
      requestId,
      row
    });
  });

  $('#select-all-requests').on('change', function() {
    $('.request-checkbox').prop('checked', this.checked);
  });

  $('.bulk-auto-assign-btn').on('click', function() {
    const selectedRows = $('.request-checkbox:checked').closest('tr');
    if (selectedRows.length === 0) {
      showErrorBanner('Please select at least one request to auto-assign.');
      return;
    }

    const requestIds = selectedRows.map(function() {
      return $(this).data('request-id');
    }).get();

    showAssignConfirmation('bulk', {
      requestIds,
      selectedRows,
      count: selectedRows.length
    });
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