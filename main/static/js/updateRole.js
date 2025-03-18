// Update user role in the database

$(document).ready(function() {
  $('.update-role-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const userId = row.data('user-id');
    const select = row.find('.role-select')
    const newRole = row.find('.role-select').val();

    if (newRole === '3') {
      if (!confirm('Are you sure you want to make this user a manager? This action cannot be undone.')) {
        return;
      }
    }
      
    try {
      const response = await csrfFetch(`/dashboard/api/users/${userId}/role`, {
        method: 'PATCH',
        body: JSON.stringify({ role: parseInt(newRole) })
      });
          
      const data = await response.json();
      
      // Cannot edit managers, remove from table
      if (newRole === '3') {
        row.remove(); 
      } else if (data && data.new_role) {
        const roleText = data.new_role === 2 ? 'Expert' : 'User';
        row.find('.role-cell').text(roleText);
        row.find('.updated-cell').text(data.updated_at);
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });
});