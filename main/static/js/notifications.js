$(document).ready(function() {
  const userKey = $('meta[name="user-key"]').attr('content');
  
  if (!userKey) {
    return; // Not logged in
  }
  
  // Join a personal room for receiving notifications
  window.globalSocket.emit('join_user', { 'user_key': userKey });
  
  // Handle incoming notifications
  window.globalSocket.on('new_notification', function(data) {
    console.log('New notification:', data);
    // Update notification badge count
    const badgeElement = $('.btn-light .badge');
    
    if (badgeElement.length) {
      const currentCount = parseInt(badgeElement.text());
      badgeElement.text(currentCount + 1);
    } else {
      // Create new badge if doesn't exist
      const newBadge = $('<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">1</span>');
      $('.btn-light').append(newBadge);
    }
      
    // Add new notification to dropdown
    const dropdownMenu = $('.dropdown-menu');
    const noNotifsItem = dropdownMenu.find('.dropdown-item:contains("No notifications")');
    
    if (noNotifsItem.length) {
      // Replace "No notifications" message
      noNotifsItem.parent().remove();
    }
      
    // Create notification item
    let notificationHTML = '<li>';
      
    if (data.item_url) {
      notificationHTML += `<a href="/item/${data.item_url}" class="dropdown-item fw-bold text-decoration-none">
        <small class="text-muted d-block">${data.created_at}</small>
        ${data.message}
      </a>`;
    } else {
      notificationHTML += `<div class="dropdown-item fw-bold">
        <small class="text-muted d-block">${data.created_at}</small>
        ${data.message}
      </div>`;
    }
      
    notificationHTML += '</li>';
      
    // Add to the top of the list
    dropdownMenu.prepend(notificationHTML);
      
    // Display a toast notification
    showToast(data.message);
  });
  
  // Display a toast notification
  function showToast(message) {
    // Create toast container if it doesn't exist
    if ($('#toast-container').length === 0) {
      $('body').append('<div id="toast-container" class="position-fixed top-0 end-0 p-3" style="z-index: 1050;"></div>');
    }
      
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
      <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
          <strong class="me-auto">Notification</strong>
          <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${message}</div>
      </div>
    `;
      
    $('#toast-container').append(toastHTML);
      
    const toastElement = new bootstrap.Toast(document.getElementById(toastId), {
      autohide: true,
      delay: 5000
    });
      
    toastElement.show();
  }
});