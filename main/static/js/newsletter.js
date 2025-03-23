$(document).ready(function() {
  const emailInput = $('#newsletter-email');
  const subscribeBtn = $('#newsletter-subscribe');
  const feedbackContainer = $('.newsletter-feedback');
  
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  
  subscribeBtn.on('click', function() {
    const email = emailInput.val().trim();

    feedbackContainer.removeClass('text-danger text-success').text('');
    
    // Validate email
    if (!email) {
      feedbackContainer.addClass('text-danger').text('Email address is required');
      return;
    }
    
    if (!validateEmail(email)) {
      feedbackContainer.addClass('text-danger').text('Please enter a valid email address');
      return;
    }
    
    // Simulate a server request with using setTimeout
    subscribeBtn.prop('disabled', true).text('Subscribing...');
    
    setTimeout(function() {
      // Success - update UI
      emailInput.prop('disabled', true)
                .css({
                  'background-color': '#e9ecef',
                  'color': '#6c757d',
                  'border-color': '#ced4da'
                })
                .val('Subscribed: ' + email);
      
      subscribeBtn.prop('disabled', true)
                  .removeClass('btn-accent')
                  .addClass('btn-secondary')
                  .text('Subscribed');
      
      feedbackContainer.addClass('text-success')
                       .text('Thank you for subscribing to our newsletter!');
    }, 1000);
  });
  
  // Also allow form submission with Enter key
  emailInput.on('keypress', function(e) {
    if (e.which === 13) {
      e.preventDefault();
      subscribeBtn.click();
    }
  });
});
