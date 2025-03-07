$(document).ready(function() {
    // Watch button functionality
    $('#watch-btn').on('click', function(e) {
      // Prevent default action and stop propagation to avoid form submission
      e.preventDefault();
      e.stopPropagation();
      
      const itemUrl = $(this).data('item-url');
      
      csrfFetch(`/item/${itemUrl}/watch`, {
        method: 'POST'
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          // Change button to watched (not unwatch)
          $(this).replaceWith(`
            <button id="unwatch-btn" class="btn btn-success" data-item-url="${itemUrl}">
              <i class="fas fa-check"></i> Watched
            </button>
          `);
          
          // Update the watch counter
          if ($('#watch-counter').length) {
            const currentCount = parseInt($('#watch-counter').text().match(/\d+/)[0]);
            const newCount = currentCount + 1;
            $('#watch-counter').html(`
              <i class="fas fa-user-friends"></i> ${newCount} ${newCount === 1 ? 'watcher' : 'watchers'}
            `);
          }
          
          // Add event listener for the new unwatch button
          $('#unwatch-btn').on('click', function(e) {
            // Prevent default action and stop propagation to avoid form submission
            e.preventDefault();
            e.stopPropagation();
            handleUnwatch($(this));
          });
        } else {
          alert(data.error || 'Error watching auction');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Error watching auction. Please try again.');
      });
    });
  
    // Unwatch button functionality
    $('#unwatch-btn').on('click', function(e) {
      // Prevent default action and stop propagation to avoid form submission
      e.preventDefault();
      e.stopPropagation();
      handleUnwatch($(this));
    });
    
    function handleUnwatch(button) {
      const itemUrl = button.data('item-url');
      
      // Create and show the confirmation modal
      if ($('#unwatchConfirmationModal').length === 0) {
        $('body').append(`
          <div class="modal fade" id="unwatchConfirmationModal" tabindex="-1" aria-labelledby="unwatchConfirmationModalLabel" aria-hidden="true">
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="unwatchConfirmationModalLabel">Confirm Unwatch</h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                  <p>Are you sure you want to unwatch this auction?</p>
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                  <button type="button" class="btn btn-danger" id="confirm-unwatch-btn">Yes, Unwatch</button>
                </div>
              </div>
            </div>
          </div>
        `);
      }
      
      // Show the modal
      const unwatchModal = new bootstrap.Modal(document.getElementById('unwatchConfirmationModal'));
      unwatchModal.show();
      
      // Handle confirm button click
      $('#confirm-unwatch-btn').off('click').on('click', function() {
        // Close the modal
        unwatchModal.hide();
        
        csrfFetch(`/item/${itemUrl}/unwatch`, {
          method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            // Change button back to watch
            button.replaceWith(`
              <button id="watch-btn" class="btn btn-outline-primary" data-item-url="${itemUrl}">
                <i class="fas fa-eye"></i> Watch
              </button>
            `);
            
            // Update the watch counter
            if ($('#watch-counter').length) {
              const currentCount = parseInt($('#watch-counter').text().match(/\d+/)[0]);
              const newCount = Math.max(0, currentCount - 1);
              $('#watch-counter').html(`
                <i class="fas fa-user-friends"></i> ${newCount} ${newCount === 1 ? 'watcher' : 'watchers'}
              `);
            }
            
            // Add event listener for the new watch button
            $('#watch-btn').on('click', function(e) {
              // Prevent default action and stop propagation to avoid form submission
              e.preventDefault();
              e.stopPropagation();
              $(this).trigger('click');
            });
          } else {
            alert(data.error || 'Error unwatching auction');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Error unwatching auction. Please try again.');
        });
      });
    }
});