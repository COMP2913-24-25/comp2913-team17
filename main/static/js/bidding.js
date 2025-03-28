// Bidding Scripts

$(document).ready(function() {
  // Disable the modal on page load
  const bidHistoryModal = document.querySelector('.bid-history-modal'); 
  if (bidHistoryModal) {
    bidHistoryModal.style.display = 'none';
  
    // Make sure Bootstrap doesn't override our display setting
    bidHistoryModal.classList.remove('show');
    document.body.classList.remove('modal-open');
  
    // Remove any backdrop that might have been added
    const backdrop = $('.modal-backdrop');
    if (backdrop) {
      backdrop.remove();
    }
  }

  const userID = $('meta[name="user-id"]').attr('content');
  const bidForm = $('.bid-form');
  const bidAmount = $('#bid_amount');
  const maxBid = $('.max-bid');
  let maxBidAlert = $('.max-bid-alert');
  let bidHistory = $('.bid-history');
  let bidCount = $('.bid-count');
  const noBids = $('.no-bids-msg');
  const auctionEnd = $('.auction-end');
  const countdown = $('.countdown');
  const shouldReload = new Date() <= new Date(countdown.data('end'));
  const currentPrice = $('#price-section');
  const bidHelp = $('#bid-amount-help');

  function showBidAlert(message, type = 'danger') {
    
    // Remove any existing alerts
    $('.bid-alert-banner').remove();
    
    // Create the alert element
    const alertEl = $(`
      <div class="alert alert-${type} bid-alert-banner alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `);
    
    if ($('.countdown-label').length) {
      $('.countdown-label').closest('.mb-4').after(alertEl);
    } else {
      $('#price-section').after(alertEl);
    }
    
    // Hide the modal after a bid
    $('.place-bid-modal').modal('hide');
    
    // Automatically close the alert after 5 seconds
    setTimeout(() => {
      alertEl.alert('close');
    }, 5000);
  }

  // Initialise live countdown
  function startCountdown() {
    if (countdown.length) {
      updateCountdown(countdown);
    
      // For less than 1 minute, countdown in seconds
      setInterval(function() {
        if (countdown.hasClass('countdown-urgent')) {
          updateCountdown(countdown);
        }
      }, 1000);
      
      // Every minute for regular countdowns
      setInterval(function() {
        if (!countdown.hasClass('countdown-urgent') && !countdown.hasClass('countdown-ended')) {
          updateCountdown(countdown);
        }
      }, 60000);
    }
  }
    
  function updateCountdown(element) {
    const endTime = element.data('end');
    const now = new Date();
    const target = new Date(endTime);
    const delta = target - now;
    
    // If auction has ended
    if (now >= target) {
      if (shouldReload) {
        location.reload();
      }
      
      return;
    }
    
    // Check if 1 minute remains
    const seconds = Math.floor(delta / 1000);
    const minutes = Math.floor(delta / (1000 * 60));
    
    // If 1 minute, add urgent class and count in seconds
    if (minutes <= 1) {
      element.removeClass('countdown-active').addClass('countdown-urgent');
      element.text(seconds + (seconds === 1 ? ' second' : ' seconds'));
    } else {
      // Otherwise, normal countdown
      element.removeClass('countdown-urgent').addClass('countdown-active');
      element.text(getTimeRemaining(endTime));
    }
  }
  
  function getTimeRemaining(datetime) {
    const now = new Date();
    const target = new Date(datetime);
    const delta = target - now;
    
    const minutes = Math.floor(delta / (1000 * 60));
    const hours = Math.floor(delta / (1000 * 60 * 60));
    const days = Math.floor(delta / (1000 * 60 * 60 * 24));
    
    if (hours < 1) {
      return minutes < 2 ? '1 minute' : `${minutes} minutes`;
    } else if (days < 1) {
      return hours < 2 ? '1 hour' : `${hours} hours`;
    } else {
      return days < 2 ? '1 day' : `${days} days`;
    }
  }
  
  startCountdown();

  // Join this auction's room if the auction is open and the user is logged in
  if (!userID) {
    return;
  }

  if (auctionEnd.length) {
    const end = new Date(auctionEnd.text());
    const now = new Date();

    if (now > end) {
      return;
    }
  }

  const itemURL = window.location.pathname.split('/').pop();
  window.globalSocket.emit('join_auction', { 'item_url': itemURL });

  // Submit a bid
if (bidForm.length) {
  bidForm.on('submit', async function(e) {
    e.preventDefault();

      const newBid = parseFloat(bidAmount.val());
      if (!newBid || isNaN(newBid)) {
        showBidAlert('Please enter a valid bid amount.', 'warning');
        return;
      }

      if (newBid <= maxBid.val()) {
        showBidAlert('Bid amount must be greater than the current bid.', 'warning');
        return;
      }
      
      try {
        const response = await csrfFetch(`/item/${itemURL}/bid`, {
          method: 'POST',
          body: JSON.stringify({ bid_amount: newBid })
        });
            
        const data = await response.json();
        if (response.status !== 200) {
          throw data;
        }
        
        // Success message after successful bid
        showBidAlert(`Your bid of £${newBid.toFixed(2)} has been placed successfully!`, 'success');
      } catch (error) {
        console.log('Error:', error);
        showBidAlert(`Error placing bid. Please try again.`, 'danger');
      }
    });
  };

  // Listen for bid updates
  window.globalSocket.on('bid_update', function(data) {
    // Update the highest bid
    if (maxBid.length) {
      maxBid.text(`${parseFloat(data.bid_amount).toFixed(2)}`);
    }

    // Update the current price
    currentPrice.html(`
      <h5>Highest Bid</h5>
      <div class="h3 text-primary">£${parseFloat(data.bid_amount).toFixed(2)}</div>
    `)

    bidHelp.html(`
      Current highest bid: £<span class="max-bid">${parseFloat(data.bid_amount).toFixed(2)}</span>
    `)

    // Update the bid history
    if (!bidHistory.length) {
      bidHistory = $('<ol class="bid-history" reversed></ol>');
      bidHistory.attr('start', 1);
      
      if (noBids.length) {
        noBids.replaceWith(bidHistory);
      }
    }

    const newBid = `
      <li style="padding: 10px;">
      <div class="bid-info-row">
        ${data.bid_username}</strong> - £${parseFloat(data.bid_amount).toFixed(2)}
        <small class='text-muted'>(${data.bid_time})</small>
      </div>
      </li>
      <hr class="full-width-hr">
    `;

    bidHistory.prepend(newBid);

    bidCount.html($(`<button href='#' class="bid-count btn btn-primary">${bidHistory.children().length / 2} bids</button>`));
    bidHistory.prop('start', bidHistory.children().length / 2);

    // Update suggested bid
    if (bidAmount.length) {
      bidAmount.val((parseFloat(data.bid_amount) + 0.01).toFixed(2));
      bidAmount.attr('min', (parseFloat(data.bid_amount) + 0.01).toFixed(2));
    }

    // Update max bid alert
    if (maxBidAlert.length && data.bid_userid.toString() === userID) {
      maxBidAlert.text(`You currently have the highest bid!`);
      maxBidAlert.show();
    // Create alert if it doesn't exist
    } else if (userID === data.bid_userid.toString()) {
      const newAlert = $('<div class="alert alert-info max-bid-alert">You currently have the highest bid!</div>');
      newAlert.insertAfter($('.small-end').first());
      maxBidAlert = $('.max-bid-alert');
    } else {
      maxBidAlert.hide();
    }
  });

  // Leave the auction room when the user navigates away
  $(window).on('beforeunload', function() {
    window.globalSocket.emit('leave', { 'item_url': itemURL });
  });

  // Disconnect the socket when the auction ends
  window.globalSocket.on('auction_ended', function(data) {
    window.globalSocket.emit('leave', { 'item_url': itemURL });
  });
});
