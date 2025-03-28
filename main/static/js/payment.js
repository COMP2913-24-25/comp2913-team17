// Retrieve the CSRF token from the meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Check for canceled payment on page load
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('payment_status') === 'canceled') {
    showErrorBanner('Payment was canceled. Your order has not been processed.');
    
    // Remove the parameter from the URL
    const url = new URL(window.location);
    url.searchParams.delete('payment_status');
    window.history.replaceState({}, '', url);
  }
});

// Function to show success banner
function showSuccessBanner(message) {
  // Remove any existing banners
  $('.success-banner').remove();
  
  // Create the banner
  const banner = $(`
    <div class="success-banner alert alert-success alert-dismissible fade show" role="alert">
      <i class="fas fa-check-circle me-2"></i>
      <strong>Success!</strong> ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `);
  
  // Add the banner to the top of the content area
  $('main').prepend(banner);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    banner.alert('close');
  }, 5000);
}

// Function to show error banner
function showErrorBanner(message) {
  // Remove any existing error banners
  $('.error-banner').remove();
  
  // Create the banner
  const banner = $(`
    <div class="error-banner alert alert-danger alert-dismissible fade show" role="alert">
      <i class="fas fa-exclamation-circle me-2"></i>
      <strong>Error!</strong> ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `);
  
  // Add the banner to the top of the content area
  $('main').prepend(banner);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    banner.alert('close');
  }, 5000);
}

// Function to show payment confirmation dialog
function showPaymentConfirmation(itemData, callback) {
  if ($('#paymentConfirmationModal').length > 0) {
    $('#paymentConfirmationModal').remove();
  }
  
  $('body').append(`
    <div class="modal fade" id="paymentConfirmationModal" tabindex="-1" aria-labelledby="paymentConfirmationModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="paymentConfirmationModalLabel">Confirm Payment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to proceed to checkout for this item?</p>
            <p>You will be redirected to Stripe's secure payment page.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" id="confirm-payment-btn">Proceed to Payment</button>
          </div>
        </div>
      </div>
    </div>
  `);
  
  const paymentModal = new bootstrap.Modal(document.getElementById('paymentConfirmationModal'));
  paymentModal.show();

  $('#confirm-payment-btn').off('click').on('click', function() {
    paymentModal.hide();
    callback();
  });
}

// Attach event listener to the "Checkout" buttons
document.querySelectorAll('.checkout-button').forEach(button => {
  button.addEventListener('click', () => {
    // Get the item URL
    const itemUrl = button.getAttribute('data-item-url');
    
    // Get the current page URL to return to after payment
    const returnUrl = window.location.href;
    
    // Create cancel URL with parameter - ensure it's a full URL
    const cancelUrl = new URL(window.location.href);
    cancelUrl.searchParams.set('payment_status', 'canceled');
    
    // Show payment confirmation dialog
    showPaymentConfirmation({itemUrl, returnUrl}, async () => {
      try {
        // Create a Checkout Session with explicit cancel URL
        const response = await fetch(`/item/${itemUrl}/create-checkout-session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify({
            'returnUrl': returnUrl,
            'cancelUrl': cancelUrl.toString()
          })
        });

        const data = await response.json();

        if (data.error) {
          showErrorBanner(data.error);
          return;
        }
        
        // Show success banner before redirect
        showSuccessBanner("Redirecting to secure payment page...");
        
        // Redirect the customer to Stripe Checkout after a short delay
        setTimeout(() => {
          window.location.href = data.checkoutUrl;
        }, 1000);
      } catch (err) {
        console.error('Error creating Checkout Session:', err);
        showErrorBanner('Error creating Checkout Session');
      }
    });
  });
});
