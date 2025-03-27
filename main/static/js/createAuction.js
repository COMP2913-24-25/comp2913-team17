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
      window.alert("Please select up to 5 images maximum");
      // Clear the uploaded files from the file selector
      this.value = "";
    } else if (images.length > 0) {
      // Render a list of the filenames with each name in its own div
      // Each div is given its own index id for targeting
      let imageNames = Array.from(images).map((image, index) => 
        `<div class="image-${index} image-item">
          <i class="delete-btn fa-solid fa-square-minus" data-index="${index}"></i>
          <span class="image-name">${image.name}</span>
         </div>`).join('\n');
      imageList.append(imageNames);
    }
  });

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
    });
  });

  // Function to calculate and display the countdown
  function updateCountdown() {
    const endTimeInput = $('#enter-end-time').val();
    const timerElement = $('#timer');

    if (!endTimeInput) {
      timerElement.text("Select a date to see the countdown");
      timerElement.removeClass('text-danger');
      return;
    }

    const endTime = new Date(endTimeInput);

    // Check if the date is invalid
    if (isNaN(endTime.getTime())) {
      timerElement.text("Invalid date format");
      timerElement.addClass('text-danger');
      return;
    }

    const now = new Date();

    if (endTime <= now) {
      timerElement.text("Auction end must be in the future");
      timerElement.addClass('text-danger');
      return;
    }

    const timeDiff = endTime - now;
    const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

    timerElement.text(`${days}d ${hours}h ${minutes}m ${seconds}s`);

    // Apply red text if less than 24 hours (24 * 60 * 60 * 1000 milliseconds)
    if (timeDiff < 24 * 60 * 60 * 1000) {
      timerElement.addClass('text-danger');
    } else {
      timerElement.removeClass('text-danger');
    }
  }

  // Event listener for changes to the auction end time input
  $('#enter-end-time').on('input', updateCountdown);

  // Update the countdown every second
  setInterval(updateCountdown, 1000);

  // Initial call to set the countdown based on the default value
  updateCountdown();
});