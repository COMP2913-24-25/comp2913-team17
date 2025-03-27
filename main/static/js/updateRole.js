// Update user role in the database

$(document).ready(function() {
  $('.update-role-btn').on('click', async function() {
    const row = $(this).closest('tr');
    const userId = row.data('user-id');
    const select = row.find('.role-select')
    const newRole = row.find('.role-select').val();

    if (newRole === '3') {
      showManagerConfirmation(row, userId, newRole);
    } else {
      updateUserRole(row, userId, newRole);
    }
  });
  
  function showManagerConfirmation(row, userId, newRole) {
    console.log("Showing manager role confirmation for user:", userId);
    
    if ($('#managerConfirmationModal').length === 0) {
      $('body').append(`
        <div class="modal fade" id="managerConfirmationModal" tabindex="-1" aria-labelledby="managerConfirmationModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="managerConfirmationModalLabel">Confirm Manager Role Assignment</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <p>Are you sure you want to make this user a manager?</p>
                <p><strong>Warning:</strong> This action cannot be undone and will give the user administrative privileges.</p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-danger" id="confirm-manager-btn">Yes, Assign Manager Role</button>
              </div>
            </div>
          </div>
        </div>
      `);
    }
    
    const managerModal = new bootstrap.Modal(document.getElementById('managerConfirmationModal'));
    managerModal.show();
    
    $('#confirm-manager-btn').off('click').on('click', function() {
      managerModal.hide();
      updateUserRole(row, userId, newRole);
    });
  }

  async function updateUserRole(row, userId, newRole) {
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
  }
});