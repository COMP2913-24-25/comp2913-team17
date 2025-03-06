$(document).ready(function() {
  // Update availability text when an expert is selected
  $('.expert-select').on('change', function() {
    var availability = $(this).find('option:selected').data('availability');
    $(this).siblings('.availability-text').text(availability);
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
      
      // Remove row on success
      if (data) {
        row.remove(); 
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });
});
