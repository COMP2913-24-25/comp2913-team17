// Mark notifications as read when dropdown is opened

document.addEventListener('DOMContentLoaded', function() {
  const notificationDropdown = document.querySelector('.notifications-dropdown');
  
  if (notificationDropdown) {
    notificationDropdown.addEventListener('show.bs.dropdown', async function() {
      try {
        await csrfFetch('/item/notifications/mark-read', {
          method: 'POST'
        });
        
        // Remove unread styling
        const unreadNotifications = this.querySelectorAll('.fw-bold');
        unreadNotifications.forEach(notification => {
          notification.classList.remove('fw-bold');
        });
        
        // Remove notification badge
        const badge = document.querySelector('.badge');
        if (badge) {
          badge.remove();
        }
      } catch (error) {
        console.error('Error marking notifications as read:', error);
      }
    });
  }
});