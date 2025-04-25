// Update user role in the database

$(document).ready(function() {
  $('.update-role-btn').on('click', async function() {
    const button = $(this);
    const originalText = button.html();
    const row = button.closest('tr');
    const userId = row.data('user-id');
    const select = row.find('.role-select');
    const newRole = select.val();
    
    // Loading animation
    button.html('<i class="fas fa-spinner fa-spin me-1"></i> Updating...');
    button.prop('disabled', true);

    if (newRole === '3') {
      if (!confirm('Are you sure you want to make this user a manager? This action cannot be undone.')) {
        // Restore button state
        button.html(originalText);
        button.prop('disabled', false);
        return;
      }
    }
      
    try {
      const response = await csrfFetch(`/dashboard/api/users/${userId}/role`, {
        method: 'PATCH',
        body: JSON.stringify({ role: parseInt(newRole) })
      });
          
      const data = await response.json();
      
      if (data && data.new_role) {
        const oldRoleValue = row.find('.role-cell .badge').hasClass('bg-success') ? 2 : 1;

        // Cannot edit managers, remove from table
        if (data.new_role === 3) {
          row.fadeOut(300, function() {
            row.remove();
            // Re-apply filters after removing row
            if (typeof window.filterDashboardUsers === 'function') {
              window.filterDashboardUsers();
            }
          });
        } else if (data.new_role === 2) {
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
        
        // Hide row if appropriate
        const roleFilter = parseInt($('#role-filter').val());
        if (roleFilter !== 0 && roleFilter !== data.new_role) {
          row.fadeOut(300);
        }
        
        // Re-apply filters after updating the row
        if (typeof window.filterDashboardUsers === 'function') {
          window.filterDashboardUsers();
        }
      } else {
        alert('Error: Unable to update user role. ' + data.error);
      }
      
      // Restore button
      button.html(originalText);
      button.prop('disabled', false);
    } catch (error) {
      console.log('Error:', error);
      
      // Restore button
      button.html(originalText);
      button.prop('disabled', false);
      alert('There was an error updating the user role. Please try again.');
    }
  });
});