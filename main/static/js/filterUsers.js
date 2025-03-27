// User filtering logic for manager dashboard

// Allow updateRole.js to call this function
window.filterDashboardUsers = function() {
  const userSearch = $('#user-search');
  const roleFilter = $('#role-filter');
  const userRows = $('.auth-card tbody tr');
  
  const searchTerm = userSearch.val().toLowerCase().trim();
  const roleValue = parseInt(roleFilter.val());
  
  let visibleRows = 0;
  
  userRows.each(function() {
    const row = $(this);
    const username = row.find('td[data-label="Username"]').text().toLowerCase();
    const email = row.find('td[data-label="Email"]').text().toLowerCase();
    
    // Get user role from the badge
    const roleCell = row.find('.role-cell');
    const isExpert = roleCell.find('.badge').hasClass('bg-success');
    const userRole = isExpert ? 2 : 1;
    
    // Apply filters
    const matchesSearch = searchTerm === '' || username.includes(searchTerm) || email.includes(searchTerm);
    const matchesRole = roleValue === 0 || userRole === roleValue;

    if (matchesSearch && matchesRole) {
      row.show();
      visibleRows++;
    } else {
      row.hide();
    }
  });
  
  // If no results, display message
  const emptyState = $('.auth-card').siblings('.empty-state-filtered');
  
  if (visibleRows === 0 && userRows.length > 0) {
    if (emptyState.length === 0) {
      $('.auth-card').after(`
        <div class="empty-state empty-state-filtered">
          <i class="fas fa-filter"></i>
          <p class="empty-state-text">No users match your search criteria.</p>
        </div>
      `);
    } else {
      emptyState.show();
    }
  } else {
    emptyState.hide();
  }
};

$(document).ready(function() {
  const userSearch = $('#user-search');
  const roleFilter = $('#role-filter');
  
  userSearch.on('input', window.filterDashboardUsers);
  roleFilter.on('change', window.filterDashboardUsers);
}); 