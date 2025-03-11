// initialise Stripe using the global publishable key.
const stripe = Stripe(window.stripePublishableKey);

// Retrieve the CSRF token from the meta tag.
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

let elements;

// initialise the Payment Element on page load.
initialise();

// Attach event listener to the "Pay Now" button.
document.getElementById('submit').addEventListener('click', handleSubmit);

async function initialise() {
  try {
    const response = await fetch(window.paymentIntentUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      }
    });
    const data = await response.json();
    if (data.error) {
      document.getElementById("payment-message").innerText = data.error;
      return;
    }
    const clientSecret = data.clientSecret;
    // initialise Stripe Elements with the client secret.
    elements = stripe.elements({ clientSecret });
    const paymentElement = elements.create("payment");
    paymentElement.mount("#payment-element");
  } catch (err) {
    console.error("Error initializing Payment Element:", err);
    document.getElementById("payment-message").innerText = "Error initializing payment form.";
  }
}

async function handleSubmit(e) {
  e.preventDefault();
  try {
    // Confirm payment with a return_url and redirect behavior.
    const { error: confirmError, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: window.redirectAfterPaymentUrl
      },
      redirect: 'if_required'
    });
    if (confirmError) {
      document.getElementById("payment-message").innerText = confirmError.message;
      return;
    }
    // If the payment succeeded, mark the item as paid.
    if (paymentIntent && paymentIntent.status === 'succeeded') {
      const markWonResponse = await fetch(window.markWonUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken
        }
      });
      const markWonData = await markWonResponse.json();
      if (markWonData.status === 'success') {
        // Redirect to the redirect_after_payment route (which will flash a success message).
        window.location.href = window.redirectAfterPaymentUrl;
      } else {
        document.getElementById("payment-message").innerText = markWonData.error || "Payment succeeded but marking item as paid failed.";
      }
    }
  } catch (err) {
    console.error("Error in handleSubmit:", err);
    document.getElementById("payment-message").innerText = "An unexpected error occurred.";
  }
}
