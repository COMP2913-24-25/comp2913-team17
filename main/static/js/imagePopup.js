function imagePopup(event) {
    // gets the url of the current focused image
    let imageSrc = event.target.src;

    // send the url to the modal
    let modalImage = document.querySelector('.modal-image');
    modalImage.src = imageSrc;

    // show the modal
    let modal = new bootstrap.Modal(document.querySelector('.image-modal'));
    modal.show();
}

$(document).ready(function () {
    $('.modal-image').on('click', function(event) {
        // stores the clicked DOM element as a jQuery object
        let clickedObject = $(this);

        // check that the image isnt already zoomed
        let isZoomed = clickedObject.hasClass('is-zoomed');

        // allows the positioning and size of the image to be read
        let imageSpace = this.getBoundingClientRect();
        
        // gets the position of the click event within the image
        let X = (event.clientX - imageSpace.left)
        let Y = (event.clientY - imageSpace.top)

        // gets the position of the click event as a percentage
        let percentX = X / imageSpace.width * 100
        let percentY = Y / imageSpace.height * 100

        clickedObject.toggleClass('is-zoomed', !isZoomed)

        // sets the transform origin to the clicked position if not already zoomed
        clickedObject.css('transform-origin', isZoomed ? 'center' : `${percentX}% ${percentY}%`)
    })
})