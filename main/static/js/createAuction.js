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

$(document).ready(function() {
  $('#upload-images').on('change', function() {
    console.log("Image upload changes");
    let images = this.files;
    let imageList = $('#image-list');
    imageList.empty();

    if (images.length > 5) {
      // Error message when user uploads more than 5 images
      window.alert("Please select up to 5 images maximum")
      // Clear the uploaded files from the file selector
      this.value = "";
    } else if (images.length > 0) {
      // Render a list of the filenames with each name in its own div
      let imageNames = Array.from(images).map(image => `<div>${image.name}</div>`).join('\n');
      imageList.append(imageNames);
    }
  });
});
