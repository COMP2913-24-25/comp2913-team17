$(document).ready(function() {
  // Update availability text when an expert is selected
  $('.expert-select').on('change', function() {
    const availability = $(this).find('option:selected').data('availability');
    $(this).closest('.d-flex.flex-column').find('.availability-text').text(availability);

    const expertise = $(this).find('option:selected').data('expertise');
    const expertiseText = $(this).closest('.d-flex').find('.expertise-text');

    // Update the coloring of the pill
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
  
  // Assign an expert to an authentication request
  $('.assign-expert-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const requestId = row.data('request-id');
    const expert = row.find('.expert-select').val();

    try {
      const response = await csrfFetch(`/dashboard/api/assign-expert/${requestId}`, {
        method: 'POST',
        body: JSON.stringify({ expert: parseInt(expert) })
      });
      const data = await response.json();
      
      if (response.ok) {
        // Remove row on success
        row.remove();

        // If there are no more rows, show the empty message
        if ($('.auth-table tbody tr').length === 0) {
          $('#auth-requests-card').replaceWith(`
            <div class="empty-state">
              <i class="fas fa-clipboard-check"></i>
              <p class="empty-state-text">No pending authentication requests at this time.</p>
            </div>
          `);
        }
      } else {
        // Show error and do not remove the row
        alert(data.error || "Error assigning expert.");
      }
    } catch (error) {
      console.log('Error:', error);
      alert("Error assigning expert.");
    }
  });
});