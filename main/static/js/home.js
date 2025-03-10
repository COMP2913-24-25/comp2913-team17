// Home page scripts

$(document).ready(function() {
  // Initial update of all countdowns
  $('.countdown').each(function() {
    updateCountdown($(this));
  });
  
  // Update urgent countdowns every second
  setInterval(function() {
    $('.countdown-urgent').each(function() {
      updateCountdown($(this));
    });
  }, 1000);
  
  // Update other countdowns every minute
  setInterval(function() {
    $('.countdown').not('.countdown-urgent, .countdown-ended').each(function() {
      updateCountdown($(this));
    });
  }, 60000);
  
  // Function to apply all filters
  function applyFilters() {
    const searchTerm = $('#search-bar').val().toLowerCase().trim();
    const categoryFilter = $('#category-filter').val();
    const typeFilter = $('#type-filter').val();
    const authenticatedOnly = $('#authenticated-only').is(':checked');
    
    let visibleItems = 0;
    
    $('.auction-grid').each(function() {
      const title = $(this).data('title').toLowerCase();
      const category = $(this).find('.category').data('category');
      const auctionEndElement = $(this).find('.countdown');
      const isEnded = auctionEndElement.hasClass('countdown-ended');
      const authStatus = $(this).find('.authentication-status').data('authentication');
      
      // Type filter: 1 = Live Auctions, 2 = Ended Auctions
      let passesTypeFilter = true;
      if (typeFilter === "1") {
        passesTypeFilter = !isEnded;
      } else if (typeFilter === "2") {
        passesTypeFilter = isEnded;
      }
      
      // Category filter
      let passesCategoryFilter = true;
      if (categoryFilter && categoryFilter !== "") {
        passesCategoryFilter = (category == categoryFilter);
      }

      // Authentication filter, 2 = Authenticated
      let passesAuthFilter = true;
      if (authenticatedOnly) {
        passesAuthFilter = (authStatus == 2);
      }
      
      // Search term filter
      let passesSearchFilter = true;
      if (searchTerm !== "") {
        passesSearchFilter = title.includes(searchTerm);
      }
      
      // Show/hide based on all filters
      if (passesTypeFilter && passesCategoryFilter && passesAuthFilter && passesSearchFilter) {
        $(this).show();
        visibleItems++;
      } else {
        $(this).hide();
      }
    });
    
    // Show or hide the "no results" message
    if (visibleItems === 0) {
      $('#no-results').removeClass('d-none');
    } else {
      $('#no-results').addClass('d-none');
    }
  }
  
  // Event listeners for filters
  $('#search-bar').on('input', function() {
    applyFilters();
  });
  
  $('#category-filter').on('change', function() {
    applyFilters();
  });
  
  $('#type-filter').on('change', function() {
    applyFilters();
  });

  $('#authenticated-only').on('change', function() {
    applyFilters();
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
    
    // If less than 1 minute, make urgent and show seconds
    if (minutes <= 1) {
      element.removeClass('countdown-active').addClass('countdown-urgent');
      element.text('Ends in ' + (seconds + (seconds === 1 ? ' second' : ' seconds')));
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
      return 'Ends in ' + (minutes < 2 ? '1 minute' : `${minutes} minutes`);
    } else if (days < 1) {
      return 'Ends in ' + (hours < 2 ? '1 hour' : `${hours} hours`);
    } else {
      return 'Ends in ' + (days < 2 ? '1 day' : `${days} days`);
    }
  }
});