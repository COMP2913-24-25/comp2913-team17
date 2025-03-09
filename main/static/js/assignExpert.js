// Assign an expert to an authentication request

$(document).ready(function() {
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