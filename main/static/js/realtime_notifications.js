document.addEventListener('DOMContentLoaded', function() {
    if (typeof io !== 'undefined') {
      // Connect to the WebSocket server
      const socket = io();

      // Listen for new notifications
      socket.on('new_notification', function(data) {
        // Update the notification count badge
        const badge = document.querySelector('.position-relative .badge');
        if (badge) {
          badge.textContent = parseInt(badge.textContent || 0) + 1;
        } else {
          const button = document.querySelector('.nav-item.dropdown button');
          if (button) {
            const newBadge = document.createElement('span');
            newBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
            newBadge.textContent = '1';
            button.appendChild(newBadge);
          }
        }

        // Add notification to the dropdown list
        const notificationList = document.querySelector('.dropdown-menu');
        if (notificationList) {
          const newItem = document.createElement('li');

          if (data.item_url) {
            newItem.innerHTML = `
              <a href="/item/${data.item_url}" class="dropdown-item fw-bold text-decoration-none">
                <small class="text-muted d-block">${new Date().toLocaleString()}</small>
                ${data.message}
              </a>
            `;
          } else {
            newItem.innerHTML = `
              <div class="dropdown-item fw-bold">
                <small class="text-muted d-block">${new Date().toLocaleString()}</small>
                ${data.message}
              </div>
            `;
          }

          // Add as the first child
          if (notificationList.firstChild) {
            notificationList.insertBefore(newItem, notificationList.firstChild);
          } else {
            notificationList.appendChild(newItem);
          }

          // Show a toast notification
          const toast = new bootstrap.Toast(createToast(data));
          toast.show();
        }
      });

      function createToast(data) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
          const container = document.createElement('div');
          container.id = 'toast-container';
          container.className = 'toast-container position-fixed top-0 end-0 p-3';
          document.body.appendChild(container);
        }

        const toastEl = document.createElement('div');
        toastEl.className = 'toast';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        toastEl.innerHTML = `
          <div class="toast-header">
            <strong class="me-auto">New Notification</strong>
            <small>${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
          </div>
          <div class="toast-body">
            ${data.message}
          </div>
        `;

        document.getElementById('toast-container').appendChild(toastEl);
        return toastEl;
      }
    }
  });