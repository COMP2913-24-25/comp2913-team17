// Add this to your existing dashboard.js or create a new file

$(document).ready(function() {
  // Update all countdowns on load
  $('.countdown').each(function() {
    updateCountdown($(this));
  });
  
  // Update countdowns every minute
  setInterval(function() {
    $('.countdown').not('.countdown-ended').each(function() {
      updateCountdown($(this));
    });
  }, 60000);
  
  // Update urgent countdowns (less than 1 hour) every second
  setInterval(function() {
    $('.countdown-urgent').each(function() {
      updateCountdown($(this));
    });
  }, 1000);
  
  // Handle unwatch buttons in the dashboard with confirmation popup
  $('.unwatch-btn').on('click', function(e) {
    e.preventDefault();
    
    const btn = $(this);
    const itemUrl = btn.data('item-url');
    const itemTitle = btn.closest('tr').find('td:first').text().trim();
    const row = btn.closest('tr');
    
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
                <p class="fw-bold" id="auction-title"></p>
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
    
    // Set the auction title in the modal
    $('#auction-title').text(itemTitle);
    
    // Show the modal
    const unwatchModal = new bootstrap.Modal(document.getElementById('unwatchConfirmationModal'));
    unwatchModal.show();
    
    // Handle confirm button click
    $('#confirm-unwatch-btn').off('click').on('click', function() {
      // Close the modal
      unwatchModal.hide();
      
      // Perform the unwatch action
      csrfFetch(`/item/${itemUrl}/unwatch`, {
        method: 'POST'
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          // Remove the row with animation
          row.fadeOut(500, function() {
            $(this).remove();
            
            // If no more watched items, show the empty message
            if ($('.unwatch-btn').length === 0) {
              $('.table-responsive').replaceWith(`
                <div class="alert alert-info">
                  <p>You are not watching any auctions. Browse active auctions to find items to watch!</p>
                  <a href="${window.location.origin}/" class="btn btn-primary">Browse Auctions</a>
                </div>
              `);
            }
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
  });
  
  function updateCountdown(element) {
    const endTime = element.data('end');
    const now = new Date();
    const target = new Date(endTime);
    const delta = target - now;
    
    // If auction has ended
    if (now >= target) {
      element.text('Auction ended');
      element.removeClass('countdown-active countdown-urgent').addClass('countdown-ended');
      return;
    }
    
    const seconds = Math.floor(delta / 1000);
    const minutes = Math.floor(delta / (1000 * 60));
    const hours = Math.floor(delta / (1000 * 60 * 60));
    const days = Math.floor(delta / (1000 * 60 * 60 * 24));
    
    // If less than 1 hour, make urgent and show minutes
    if (hours < 1) {
      element.removeClass('countdown-active').addClass('countdown-urgent');
      element.text(minutes + (minutes === 1 ? ' minute' : ' minutes'));
    } else if (days < 1) {
      // Less than a day, show hours
      element.removeClass('countdown-urgent').addClass('countdown-active');
      element.text(hours + (hours === 1 ? ' hour' : ' hours'));
    } else {
      // More than a day, show days
      element.removeClass('countdown-urgent').addClass('countdown-active');
      element.text(days + (days === 1 ? ' day' : ' days'));
    }
  }
});