// Cookie Consent Popup Script

document.addEventListener('DOMContentLoaded', function() {
    // Check if user has already made a cookie choice
    const cookieConsent = localStorage.getItem('cookieConsent');
    const cookiePopup = document.getElementById('cookie-consent-popup');
    
    // Remove the popup element completely if user has already made a choice
    if (cookieConsent && cookiePopup) {
      cookiePopup.parentNode.removeChild(cookiePopup);
    } else if (!cookieConsent && cookiePopup) {
      // Show the popup after a short delay if no choice has been made yet
      setTimeout(() => {
        cookiePopup.classList.add('show');
      }, 1000);
      
      // Handle Accept button click
      document.getElementById('accept-cookies').addEventListener('click', function() {
        acceptCookies(true);
      });
      
      // Handle Reject button click
      document.getElementById('reject-cookies').addEventListener('click', function() {
        acceptCookies(false);
      });
    }
    
    function acceptCookies(accepted) {
      // Save user's choice to localStorage
      localStorage.setItem('cookieConsent', accepted ? 'accepted' : 'rejected');
      
      // Hide the popup with animation
      cookiePopup.classList.remove('show');
      
      // Remove element completely from the DOM after animation completes
      setTimeout(() => {
        if (cookiePopup && cookiePopup.parentNode) {
          cookiePopup.parentNode.removeChild(cookiePopup);
        }
      }, 300);
    }
});
