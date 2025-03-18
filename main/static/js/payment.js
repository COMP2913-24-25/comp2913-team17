// Retrieve the CSRF token from the meta tag.
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Attach event listener to the "Checkout" button.
document.getElementById('checkout-button').addEventListener('click', async () => {
  try {
    const response = await fetch(window.createCheckoutSessionUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({})  // No extra data required
    });
    const data = await response.json();
    if (data.error) {
      document.getElementById("payment-message").innerText = data.error;
      return;
    }
    // Redirect the customer to Stripe Checkout.
    window.location.href = data.checkoutUrl;
  } catch (err) {
    console.error("Error creating Checkout Session:", err);
    document.getElementById("payment-message").innerText = "An error occurred.";
  }
});
