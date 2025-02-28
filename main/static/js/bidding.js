$(document).ready(function() {
  const userID = $('meta[name="user-id"]').attr('content');
  const bidForm = $('.bid-form');
  const bidAmount = $('#bid_amount');
  const bidHistory = $('.bid-history');
  const maxBid = $('.max-bid');
  let maxBidAlert = $('.max-bid-alert');
  const auctionEnd = $('.auction-end');
  
  // Join this auction's room if the auction is open and the user is logged in
  if (!userID) {
    return;
  }

  if (auctionEnd.length) {
    const end = new Date(auctionEnd.text());
    const now = new Date();

    if (now > end) {
      bidForm.hide();
      maxBidAlert.hide();
      bidAmount.prop('disabled', true);
      bidAmount.attr('title', 'Auction has ended');
      return;
    }
  }

  const socket = io();
  const itemURL = window.location.pathname.split('/').pop();
  socket.emit('join', { 'item_url': itemURL });

  // Submit a bid
  if (bidForm.length) {
    bidForm.on('submit', async function(e) {
      e.preventDefault();

      const newBid = parseFloat(bidAmount.val());
      if (!newBid || isNaN(newBid)) {
        alert('Please enter a valid bid amount.');
        return;
      }

      if (newBid <= maxBid.val()) {
        alert('Bid amount must be greater than the current bid.');
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
      } catch (error) {
        console.log('Error:', error);
        alert(`Error placing bid. Please try again.`);
      }
    });
  };

  // Listen for bid updates
  socket.on('bid_update', function(data) {
    // Update the highest bid
    if (maxBid.length) {
      maxBid.text(`${parseFloat(data.bid_amount).toFixed(2)}`);
    }

    // Update the bid history
    if (bidHistory.length) {
      bidHistory.prepend(`
        <li>
          ${data.bid_username}</strong> - £${parseFloat(data.bid_amount).toFixed(2)}
          <small class="text-muted">(${data.bid_time})</small>
        </li>
      `);
      bidHistory.prop('start', bidHistory.children().length);
    }

    // Update suggested bid
    if (bidAmount.length) {
      bidAmount.val((parseFloat(data.bid_amount) + 0.01).toFixed(2));
      bidAmount.attr('min', (parseFloat(data.bid_amount) + 0.01).toFixed(2));
    }

    // Update max bid alert
    if (maxBidAlert.length && data.bid_userid.toString() === userID) {
      maxBidAlert.text(`You currently have the highest bid.`);
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
    socket.emit('leave', { 'item_url': itemURL });
  });
});