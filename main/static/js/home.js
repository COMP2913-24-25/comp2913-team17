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
  
  // Function to apply filters and sorting
  function applyFiltersAndSort() {
    const searchTerm = $('#search-bar').val().toLowerCase().trim();
    const categoryFilter = $('#category-filter').val();
    const typeFilter = $('#type-filter').val();
    const authenticatedOnly = $('#authenticated-only').is(':checked');
    const sortOption = $('#sort-filter').val();
    
    let items = $('.auction-grid-wrapper').get(); // Get all items as an array
    let visibleItems = 0;

    $('#auction-type').text(typeFilter === "1" ? "Live Auctions" : typeFilter === "2" ? "Ended Auctions" : "All Auctions");
    
    // Filter items
    items.forEach(function(item) {
      const $item = $(item);
      const title = $item.data('title').toLowerCase();
      const category = $item.find('.category').data('category');
      const auctionEndElement = $item.find('.countdown');
      const isEnded = auctionEndElement.hasClass('countdown-ended');
      const authStatus = $item.find('.authentication-status').data('authentication');
      
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
        $item.css('display', '');
        visibleItems++;
      } else {
        $item.css('display', 'none');
      }
    });
    
    // Only sort and rearrange if there are items to show
    if (visibleItems > 0) {
      // Sort visible items
      items.sort(function(a, b) {
        const $a = $(a);
        const $b = $(b);
        const isAVisible = $a.css('display') !== 'none';
        const isBVisible = $b.css('display') !== 'none';
        
        // Prioritize visible items
        if (isAVisible && !isBVisible) return -1;
        if (!isAVisible && isBVisible) return 1;
        if (!isAVisible && !isBVisible) return 0;
        
        // Both visible, apply sorting
        switch (sortOption) {
          case 'price-low-high':
            return parseFloat($a.data('price')) - parseFloat($b.data('price'));
          case 'price-high-low':
            return parseFloat($b.data('price')) - parseFloat($a.data('price'));
          case 'ending-soonest':
            const isAEnded = $a.find('.countdown').hasClass('countdown-ended');
            const isBEnded = $b.find('.countdown').hasClass('countdown-ended');
            // If one is ended and the other isn't, ended goes to the bottom
            if (isAEnded && !isBEnded) return 1;
            if (!isAEnded && isBEnded) return -1;
            // Both active or both ended, sort by end time ascending
            return new Date($a.data('end')) - new Date($b.data('end'));
          case 'ending-latest':
            return new Date($b.data('end')) - new Date($a.data('end'));
          case 'title-a-z':
            return $a.data('title').localeCompare($b.data('title'));
          default:
            return 0;
        }
      });
      
      // Re-append sorted items to container without affecting animation
      const $container = $('#auction-container');
      // Store the current scroll position
      const scrollTop = $(window).scrollTop();
      
      // Detach all items
      const $items = $('.auction-grid-wrapper').detach();
      
      // Re-append in sorted order
      items.forEach(function(item) {
        $container.append(item);
      });
      
      // Restore scroll position to prevent jumps
      $(window).scrollTop(scrollTop);
    }
    
    // Display "no results" message as appropriate
    if (visibleItems === 0) {
      $('#no-results').removeClass('d-none');
    } else {
      $('#no-results').addClass('d-none');
    }
  }
  
  // Event listeners for filters and sorting
  $('#search-bar').on('input', applyFiltersAndSort);
  $('#category-filter').on('change', applyFiltersAndSort);
  $('#type-filter').on('change', applyFiltersAndSort);
  $('#authenticated-only').on('change', applyFiltersAndSort);
  $('#sort-filter').on('change', applyFiltersAndSort);
  
  function updateCountdown(element) {
    const endTime = element.data('end');
    const now = new Date();
    const target = new Date(endTime);
    const delta = target - now;
    
    // If auction has ended
    if (now >= target) {
      element.text('Auction ended');
      element.removeClass('countdown-active countdown-urgent').addClass('countdown-ended');

      // If the authentication was pending, then it's been cancelled
      const authStatusElement = element.closest('.auction-info').find('.authentication-status');
      
      if (authStatusElement.data('authentication') == 1) {
        authStatusElement.attr('data-authentication', '4');
        authStatusElement.removeClass('bg-warning').addClass('bg-secondary');
        authStatusElement.html('<i class="fas fa-question-circle me-1"></i> NOT AUTHENTICATED');
      }
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

  // Hero typing effect
  const wordElement = $('#rotating-word');
  const containerElement = $('#rotating-word-container');
  const categoryNames = [
    'ANTIQUES.',
    'ART.',
    'BOOKS.',
    'COLLECTIBLES.',
    'ELECTRONICS.',
    'FASHION.',
    'FURNITURE.',
    'INSTRUMENTS.',
    'TOYS.',
    'VEHICLES.',
    'TREASURES.'
  ];

  if (wordElement.length && containerElement.length && categoryNames.length) {
    // Set minimum width to accommodate the longest word
    let longestCat = '';
    for (const category of categoryNames) {
      if (category.length > longestCat.length) {
        longestCat = category;
      }
    }
    containerElement.css('min-width', ((longestCat.length + 20) * 20) + 'px');
    
    // Initialise with the first word already displayed
    let currentWordIndex = 0;
    let isDeleting = true;
    let currentText = 'TREASURES.';
    let typingSpeed = 100;
    let isFirstCycle = true;
    
    function typeEffect() {
      const currentWord = categoryNames[currentWordIndex];
      
      if (isDeleting) {
        // Deleting text
        currentText = currentText.substring(0, currentText.length - 1);
        typingSpeed = 75;
      } else {
        // Typing text
        currentText = currentWord.substring(0, currentText.length + 1);
        typingSpeed = 150;
      }

      // Ensure element never displays as completely empty or the layout will break
      const displayText = currentText === '' ? '\u200B' : currentText;
      wordElement.text(displayText);
      
      // Word cycling logic
      if (!isDeleting && currentText === currentWord) {
        // Finished typing the word, pause for 5s then start deleting
        typingSpeed = 5000;
        isDeleting = true;
      } else if (isDeleting && currentText === '') {
        isDeleting = false;
        
        if (isFirstCycle) {
          isFirstCycle = false;
        } else {
          currentWordIndex = (currentWordIndex + 1) % categoryNames.length;
        }
        typingSpeed = 500;
      }
      setTimeout(typeEffect, typingSpeed);
    }
    
    setTimeout(typeEffect, 1500);
  }

  AOS.init({
    once: false,
    disable: false,
    duration: 800,
    startEvent: 'DOMContentLoaded',
    offset: 50
  });
  
  // Make sure AOS is initialised properly after all content is loaded
  window.addEventListener('load', function() {
    setTimeout(function() {
      AOS.refresh();
    }, 500);
  });
  
  // Refresh AOS when changing orientation
  window.addEventListener('orientationchange', function() {
    setTimeout(function() {
      AOS.refresh();
    }, 300);
  });
  
  // Reveal animations on scroll
  function reveal() {
    const reveals = document.querySelectorAll('.reveal');
    const windowHeight = window.innerHeight;
    
    for (let i = 0; i < reveals.length; i++) {
      const revealTop = reveals[i].getBoundingClientRect().top;
      const revealPoint = 150;
      
      if (revealTop < windowHeight - revealPoint) {
        reveals[i].classList.add('active');
      }
    }
  }
  
  window.addEventListener('scroll', reveal);
  reveal();
  
  // Set default to live auctions
  $('#type-filter').val('1');
  $('#auction-type').text('Live Auctions');
  applyFiltersAndSort();
});