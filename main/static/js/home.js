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