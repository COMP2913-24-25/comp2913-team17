// Check if the user wants to authenticate the item before submitting the form
const authFee = $('meta[name="auth-fee"]').attr('content');

$('#create-auction-form').on('submit', (e) => {
  if ($('#authenticate-item').is(':checked')) {
    if (!confirm(
      'Are you sure you want to submit an authentication request?\n\n' +
      `The final fee will be ${authFee}% of the final sale price if the item is authenticated.`
    )) {
      e.preventDefault();
    }
  }
})