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
      // Each div is given its own index id for targetting
      let imageNames = Array.from(images).map((image, index) => 
        `<div class="image-${index} image-item">
          <i class="delete-btn fa-solid fa-square-minus" data-index="${index}"></i>
          <span class="image-name">${image.name}</span>
         </div>`).join('\n');
      imageList.append(imageNames);
    }
  });
});

$(document).ready(function() {
  /*
   * Delete buttons are not rendered until user selects images
   * attach event to parent window and target delete buttons
   * to attach the click events 
   */
  $(document).on('click', '.delete-btn', function() {
    // Target the image element using its index
    let index = $(this).data('index');
    // Removes the list element corresponding to the image
    $(`.image-${index}`).remove();

    let input = $('#upload-images')[0];
    let newList = new DataTransfer();

    Array.from(input.files).forEach((image, i) => {
      if (i !== index) {
        newList.items.add(image);
      }
    });
    input.files = newList.files;

    // Update the index of each image with the newList index values
    $('#image-list').children().each(function(newIndex, element) {
      // Remove the old image-index class
      $(element).removeClass();
      // Add the new image-index class
      $(element).addClass(`image-${newIndex} image-item`);
      // Update the data index of each delete button
      $(element).find('.delete-btn').data('index', newIndex);
    })
  })
})