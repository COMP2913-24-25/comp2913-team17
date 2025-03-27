// Update management configuration settings in the database

$(document).ready(function() {
  $('.update-base-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const newVal = row.find('.base-input').val();

    if (newVal < 0 || newVal > 100) {
      row.find('.base-input').val(row.find('.base-cell').text());
      alert('Invalid base fee: must be between 0 and 100');
      return;
    }
      
    try {
      const response = await csrfFetch(`/dashboard/api/update-base`, {
        method: 'PUT',
        body: JSON.stringify({ fee: parseFloat(newVal) })
      });
          
      const data = await response.json();
      
      if (data && data.config_key == 'base_platform_fee' && data.config_value) {
        row.find('.base-cell').text(data.config_value);
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });

  $('.update-auth-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const newVal = row.find('.auth-input').val();

    if (newVal < 0 || newVal > 100) {
      row.find('.auth-input').val(row.find('.auth-cell').text());
      alert('Invalid authentication fee: must be between 0 and 100');
      return;
    }
      
    try {
      const response = await csrfFetch(`/dashboard/api/update-auth`, {
        method: 'PUT',
        body: JSON.stringify({ fee: parseFloat(newVal) })
      });
          
      const data = await response.json();
      
      if (data && data.config_key == 'authenticated_platform_fee' && data.config_value) {
        row.find('.auth-cell').text(data.config_value);
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });

  $('.update-dur-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const newVal = row.find('.dur-input').val();

    if (newVal < 1) {
      row.find('.dur-input').val(row.find('.dur-cell').text());
      alert('Invalid auction duration: must be at least 1 day');
      return;
    }
      
    try {
      const response = await csrfFetch(`/dashboard/api/update-dur`, {
        method: 'PUT',
        body: JSON.stringify({ days: parseInt(newVal) })
      });
          
      const data = await response.json();
      
      if (data && data.config_key == 'max_auction_duration' && data.config_value) {
        row.find('.dur-cell').text(data.config_value);
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });
});