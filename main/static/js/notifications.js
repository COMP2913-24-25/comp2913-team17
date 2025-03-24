$(document).ready(function() {
  const userKey = $('meta[name="user-key"]').attr('content');
  if (!userKey) return;

  window.globalSocket = window.globalSocket || io();
  window.globalSocket.emit('join_user', { user_key: userKey });
  window.globalSocket.on('new_notification', function(data) {
    // If we are on the authentication page and receive a notification, then don't show and mark as read
    const itemUrl = $('#item-link').attr('href');

    if (itemUrl && data.item_url && itemUrl.split('/').pop() === data.item_url) {
      // Mark the notification as read without showing it
      if (data.id) {
        markNotificationsAsRead([data.id])
          .catch(error => console.error('Error marking current item notification as read:', error));
      }
      return;
    }

    // Update notification count badge
    const badge = $('#notif-button .badge');

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
      // Normal notification
      notificationElement = `
        <li>
          <a href="/item/${data.item_url}" 
             class="dropdown-item fw-bold text-decoration-none notification-item" 
             data-notification-id="${data.id || ''}">
            <small class="text-muted d-block">${data.created_at}</small>
            ${data.message}
          </a>
        </li>
      `;
    } else {
      // Welcome notification
      notificationElement = `
        <li>
          <div class="dropdown-item fw-bold notification-item" data-notification-id="${data.id || ''}">
            <small class="text-muted d-block">${data.created_at}</small>
            ${data.message}
          </div>
        </li>
      `;
    }

    // Add notification to the dropdown menu
    const notificationList = $('#notification-list');
    
    // Remove "No new notifications" message if it exists
    notificationList.find(':contains("No new notifications")').parent().remove();
    
    // Add new notification at the top
    notificationList.prepend(notificationElement);
  });

  // Mark notifications as read when clicked
  $(document).on('click', '.notification-item', function(event) {
    // For notification items with an href (links to items)
    if ($(this).attr('href')) {
      event.preventDefault();
      
      // Store the destination URL and notification ID
      const destinationUrl = $(this).attr('href');
      const notificationId = $(this).data('notification-id');
      
      if (notificationId) {
        // Mark as read, then navigate
        markNotificationsAsRead([notificationId])
          .then(() => {
            $(this).removeClass('fw-bold');
            window.location.href = destinationUrl;
          })
          .catch(error => {
            console.error('Error marking notification as read:', error);
            window.location.href = destinationUrl;
          });
      } else {
        // If no ID, just navigate
        window.location.href = destinationUrl;
      }
    } else {
      const notificationId = $(this).data('notification-id');
      if (notificationId) {
        markNotificationsAsRead([notificationId]);
        $(this).removeClass('fw-bold');
      }
    }
  });

  // Mark all notifications as read when dropdown is opened
  $('#notif-button').closest('.dropdown').on('shown.bs.dropdown', function() {
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
      
      // Make sure badge is hidden
      const badge = $('#notif-button').find('.badge');
      if (badge.length > 0) {
        badge.text('');
        badge.addClass('d-none');
      }
    }
  });

  // Clear all notifications when clear all button is clicked
  $(document).on('click', '#clear-all-notifications', function(event) {
    event.preventDefault();
    
    clearAllNotifications()
      .then(() => {
        // Hide the badge
        const badge = $('#notif-button').find('.badge');
        if (badge.length > 0) {
          badge.text('');
          badge.addClass('d-none');
        }

        // Get the notification dropdown menu
        const notificationList = $('#notif-button').next('.dropdown-menu');
        notificationList.empty().html('<li><div class="dropdown-item">No new notifications</div></li>');
      })
      .catch(error => console.error('Error clearing notifications:', error));
  });

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

  // Function to clear all notifications via API
  async function clearAllNotifications() {
    try {
      return await csrfFetch('/item/api/notifications/clear-all', {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error clearing all notifications:', error);
      throw error;
    }
  }
});