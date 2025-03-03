$(document).ready(function() {
    const watchBtn = $('#watch-btn');
    const unwatchBtn = $('#unwatch-btn');
    
    // Function to handle watching an auction
    watchBtn.on('click', async function() {
      const itemUrl = $(this).data('item-url');
      
      try {
        const response = await csrfFetch(`/item/${itemUrl}/watch`, {
          method: 'POST'
        });
        
        if (response.ok) {
          // Toggle buttons
          watchBtn.hide();
          if (unwatchBtn.length === 0) {
            // Create unwatch button if it doesn't exist
            const newUnwatchBtn = $(`<button id="unwatch-btn" class="btn btn-outline-secondary" data-item-url="${itemUrl}">
              <i class="fas fa-eye-slash"></i> Unwatch
            </button>`);
            watchBtn.after(newUnwatchBtn);
            window.location.reload(); // Reload to attach event handlers
          } else {
            unwatchBtn.show();
          }
        }
      } catch (error) {
        console.log('Error watching item:', error);
      }
    });
    
    // Function to handle unwatching an auction
    unwatchBtn.on('click', async function() {
      const itemUrl = $(this).data('item-url');
      
      try {
        const response = await csrfFetch(`/item/${itemUrl}/unwatch`, {
          method: 'POST'
        });
        
        if (response.ok) {
          // Toggle buttons
          unwatchBtn.hide();
          watchBtn.show();
        }
      } catch (error) {
        console.log('Error unwatching item:', error);
      }
    });
  });