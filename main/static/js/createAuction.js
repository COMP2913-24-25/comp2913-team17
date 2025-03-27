// Check if the user wants to authenticate the item before submitting the form

const authFee = $('meta[name="auth-fee"]').attr('content');

// Create authentication confirmation modal
$(document).ready(function() {
  if ($('#authConfirmationModal').length === 0) {
    $('body').append(`
      <div class="modal fade" id="authConfirmationModal" tabindex="-1" aria-labelledby="authConfirmationModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="authConfirmationModalLabel">Confirm Authentication Request</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <p>Are you sure you want to submit an authentication request?</p>
              <p>The final fee will be <strong>${authFee}%</strong> of the final sale price if the item is authenticated.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-primary" id="confirm-auth-btn">Confirm</button>
            </div>
          </div>
        </div>
      </div>
    `);
  }

  // Store the form submission for later use
  let formToSubmit = null;

  // Handle the form submission
  $('#create-auction-form').on('submit', function(e) {
    if ($('#authenticate-item').is(':checked')) {
      e.preventDefault(); // Prevent default form submission
      formToSubmit = $(this); // Store the form
      
      // Show the confirmation modal
      const authModal = new bootstrap.Modal(document.getElementById('authConfirmationModal'));
      authModal.show();
    }
  });

  // Handle the confirmation button click
  $(document).on('click', '#confirm-auth-btn', function() {
    // Hide the modal
    const authModal = bootstrap.Modal.getInstance(document.getElementById('authConfirmationModal'));
    authModal.hide();
    
    // Submit the form programmatically
    if (formToSubmit) {
      formToSubmit.off('submit'); // Remove the event handler to prevent infinite loop
      formToSubmit.submit(); // Submit the form
    }
  });
});

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