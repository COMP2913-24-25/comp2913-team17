$(document).ready(function() {
  const emailInput = $('#newsletter-email');
  const subscribeBtn = $('#newsletter-subscribe');
  const feedbackContainer = $('.newsletter-feedback');
  
  // Initalise and get the list of subscribers from local storage
  function getSubscribersList() {
    const storedList = localStorage.getItem('newsletterSubscribers');
    return storedList ? JSON.parse(storedList) : [];
  }
  
  // Add email to the subscribers list if not already subscribed
  function addSubscriber(email) {
    const subscribers = getSubscribersList();
    subscribers.push(email.toLowerCase());
    localStorage.setItem('newsletterSubscribers', JSON.stringify(subscribers));
  }
  
  // Check if email is already subscribed
  function isEmailSubscribed(email) {
    const subscribers = getSubscribersList();
    return subscribers.includes(email.toLowerCase());
  }
  
  // Validate email address
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
    
    // Check if email is already subscribed
    if (isEmailSubscribed(email)) {
      feedbackContainer.addClass('text-danger').text('This email address is already subscribed to our newsletter');
      return;
    }
    
    // Simulate a server request with using setTimeout
    subscribeBtn.prop('disabled', true).text('Subscribing...');
    
    setTimeout(function() {
      // Success - add to subscribers list
      addSubscriber(email);
      
      // Clear the input field for any new emails
      emailInput.val(''); 
      
      subscribeBtn.prop('disabled', false)
                 .text('Subscribe');
      
      feedbackContainer.addClass('text-success')
                       .text('Thank you for subscribing to our newsletter!');
    }, 1000);
  });
  
  // Allow using Enter key to submit the form
  emailInput.on('keypress', function(e) {
    if (e.which === 13) {
      e.preventDefault();
      subscribeBtn.click();
    }
  });
});
