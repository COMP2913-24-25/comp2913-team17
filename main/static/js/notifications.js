$(document).ready(function() {
  // Only proceed if the user is authenticated (has a secret key)
  const userKey = $('meta[name="user-key"]').attr('content');
  if (!userKey) return;

  // Join user's personal notification room
  window.globalSocket = window.globalSocket || io();
  window.globalSocket.emit('join_user', { user_key: userKey });

  // Listen for new notifications
  window.globalSocket.on('new_notification', function(data) {
    // If we are on the authentication page and receive a notification, then don't show and mark as read
    const itemUrl = $('#item-link').attr('href');

    if (itemUrl && itemUrl.split('/').pop() === data.item_url) {
      // Mark the notification as read without showing it
      if (data.id) {
        markNotificationsAsRead([data.id])
          .catch(error => console.error('Error marking current item notification as read:', error));
      }
      return;
    }

    // Update notification count badge
    const badge = $('.btn:contains("Notifications") .badge');

    // Create the badge if it doesn't exist
    if (badge.length === 0) {
      console.log('Creating badge');
      $('#notif-button').append(`
        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
          1
        </span>
      `);
    } else {
      const currentCount = parseInt(badge.text()) || 0;
      badge.text(currentCount + 1);
      
      if (badge.hasClass('d-none')) {
        badge.removeClass('d-none');
      }
    }

    // Create new notification element
    let notificationElement = '';
    if (data.item_url) {
      notificationElement = `
        <li>
          <a href="/item/${data.item_url}" 
             class="dropdown-item fw-bold text-decoration-none notification-item" 
             data-notification-id="${data.id}">
            <small class="text-muted d-block">${data.created_at}</small>
            ${data.message}
          </a>
        </li>
      `;
    } else {
      notificationElement = `
        <li>
          <div class="dropdown-item fw-bold notification-item" data-notification-id="${data.id}">
            <small class="text-muted d-block">${data.created_at}</small>
            ${data.message}
          </div>
        </li>
      `;
    }

    // Add notification to the dropdown menu
    const notificationList = $('.btn:contains("Notifications")').next('.dropdown-menu');
    
    // Remove "No notifications" message if it exists
    notificationList.find(':contains("No notifications")').parent().remove();
    
    // Add new notification at the top
    notificationList.prepend(notificationElement);

    // Show a toast notification
    showToast(data.message, data.item_url);
  });

  // Mark notifications as read when clicked
  $(document).on('click', '.notification-item', function(event) {
    // For notification items with an href (links to items)
    if ($(this).attr('href')) {
      // Prevent immediate navigation
      event.preventDefault();
      
      // Store the URL we'll navigate to after marking read
      const destinationUrl = $(this).attr('href');
      const notificationId = $(this).data('notification-id');
      
      if (notificationId) {
        // Mark as read, then navigate
        markNotificationsAsRead([notificationId])
          .then(() => {
            // Remove bold styling to indicate "read" status
            $(this).removeClass('fw-bold');
            // Navigate to the item page after marking as read
            window.location.href = destinationUrl;
          })
          .catch(error => {
            console.error('Error marking notification as read:', error);
            // Navigate anyway even if there was an error
            window.location.href = destinationUrl;
          });
      } else {
        // If no ID, just navigate
        window.location.href = destinationUrl;
      }
    } else {
      // For notification items without href (not clickable to navigate)
      const notificationId = $(this).data('notification-id');
      if (notificationId) {
        markNotificationsAsRead([notificationId]);
        // Remove bold styling to indicate "read" status
        $(this).removeClass('fw-bold');
      }
    }
  });

  // Mark all notifications as read when dropdown is opened
  $('.btn:contains("Notifications")').on('click', function() {
    const unreadNotifications = $('.dropdown-item.fw-bold');
    if (unreadNotifications.length === 0) return;

    const notificationIds = [];
    unreadNotifications.each(function() {
      const id = $(this).data('notification-id');
      if (id) notificationIds.push(id);
      $(this).removeClass('fw-bold');
    });

    if (notificationIds.length > 0) {
      markNotificationsAsRead(notificationIds);
      // Reset the badge count
      $('.btn:contains("Notifications") .badge').text('');
      $('.btn:contains("Notifications") .badge').addClass('d-none');
    }
  });

  // Function to mark notifications as read via API - modified to return the Promise
  async function markNotificationsAsRead(ids) {
    try {
      return await csrfFetch('/item/api/notifications/mark-read', {
        method: 'POST',
        body: JSON.stringify({ ids: ids })
      });
    } catch (error) {
      console.error('Error marking notifications as read:', error);
      throw error;
    }
  }

  // Function to show toast notification
  function showToast(message, itemUrl) {
    // Create toast container if it doesn't exist
    if ($('#toast-container').length === 0) {
      $('body').append('<div id="toast-container" class="position-fixed bottom-0 end-0 p-3" style="z-index: 1050"></div>');
    }

    // Create unique ID for the toast
    const toastId = 'toast-' + Date.now();
    
    // Create toast HTML
    let toastHtml = `
      <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
          <strong class="me-auto">Auction Notification</strong>
          <small>${new Date().toLocaleTimeString()}</small>
          <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
          ${message}
          ${itemUrl ? `<div class="mt-2"><a href="/item/${itemUrl}" class="btn btn-sm btn-primary">View Item</a></div>` : ''}
        </div>
      </div>
    `;
    
    // Add toast to container
    $('#toast-container').append(toastHtml);
    
    // Initialize and show toast
    const toastElement = new bootstrap.Toast(document.getElementById(toastId), {
      autohide: true,
      delay: 5000
    });
    toastElement.show();
    
    // Clean up toast after it's hidden
    $(`#${toastId}`).on('hidden.bs.toast', function() {
      $(this).remove();
    });
  }
});