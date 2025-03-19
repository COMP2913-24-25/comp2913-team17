document.addEventListener('DOMContentLoaded', function() {
    // Check if user has already made a cookie choice
    const cookieConsent = localStorage.getItem('cookieConsent');
    const cookiePopup = document.getElementById('cookie-consent-popup');
    
    if (!cookieConsent && cookiePopup) {
        // If no choice has been made yet, show the popup after a short delay
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
        setTimeout(() => {
            cookiePopup.style.display = 'none';
        }, 300);
        
        // If cookies are accepted, you could initialize additional tracking here
        if (accepted) {
            console.log("Cookies accepted - additional tracking can be initialized here");
            // For example: initGoogleAnalytics();
        }
    }
});
