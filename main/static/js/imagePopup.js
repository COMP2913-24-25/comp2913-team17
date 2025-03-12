function imagePopup(event) {
    // gets the url of the current focused image
    var imageSrc = event.target.src;

    // send the url to the modal
    var modalImage = document.querySelector('.modal-image');
    modalImage.src = imageSrc;

    // show the modal
    var modal = new bootstrap.Modal(document.querySelector('.image-modal'));
    modal.show();
}