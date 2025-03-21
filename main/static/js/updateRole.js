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
        if (data.new_role === 2) {
          row.find('.role-cell').html(`
            <div class="badge bg-success authentication-status">
              <i class="fas fa-user-graduate me-1"></i> EXPERT
            </div>
          `);
        } else {
          row.find('.role-cell').html(`
            <div class="badge bg-primary authentication-status">
              <i class="fas fa-user me-1"></i> USER
            </div>
          `);
        }
        row.find('.updated-cell').html(`
          <p>${data.updated_date}</p>
          <p>${data.updated_time}</p>
        `);
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });
});