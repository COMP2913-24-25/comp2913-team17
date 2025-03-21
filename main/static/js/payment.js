// Retrieve the CSRF token from the meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Attach event listener to the "Checkout" buttons
document.querySelectorAll('.checkout-button').forEach(button => {
  button.addEventListener('click', async () => {
    try {
      // Get the item URL
      const itemUrl = button.getAttribute('data-item-url');

      // Get the current page URL to return to after payment
      const returnUrl = window.location.href;

      // Create a Checkout Session
      const response = await fetch(`/item/${itemUrl}/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          'returnUrl': returnUrl
        })
      });

      const data = await response.json();

      if (data.error) {
        const errorMessage = document.getElementById('payment-message');

        if (errorMessage) {
          errorMessage.innerText = data.error;
        } else {
          alert(data.error);
        }
        return;
      }
      // Redirect the customer to Stripe Checkout.
      window.location.href = data.checkoutUrl;
    } catch (err) {
      console.error('Error creating Checkout Session:', err);
      
      const errorMessage = document.getElementById('payment-message');
      if (errorMessage) {
        errorMessage.innerText = 'Error creating Checkout Session';
      } else {
        alert('Error creating Checkout Session');
      }
    }
  });
});
