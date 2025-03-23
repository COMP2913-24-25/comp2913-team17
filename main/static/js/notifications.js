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
      $('..btn:contains("Notifications") .badge').addClass('d-none');
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
});