$(document).ready(function() {
    // Initialise properly based on server state
    const initialButton = $('#watch-btn, #unwatch-btn');

    // Use event delegation for all watch/unwatch buttons
    $(document).on('click', '#watch-btn, #unwatch-btn', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const button = $(this);
        const itemUrl = button.data('item-url');
        const isWatching = button.attr('id') === 'unwatch-btn';
        
        if (isWatching) {
            showUnwatchConfirmation(button, itemUrl);
        } else {
            watchAuction(button, itemUrl);
        }
    });
    
    function watchAuction(button, itemUrl) {   
        // Disable the button
        button.prop('disabled', true);
        
        csrfFetch(`/item/${itemUrl}/watch`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const newButton = $(`
                    <button id="unwatch-btn" class="btn btn-success btn-lg" data-item-url="${itemUrl}">
                        <i class="fas fa-check"></i> Watched
                    </button>
                `);
                button.replaceWith(newButton);
                
                // Update the watch counter if it exists
                if ($('#watch-counter').length) {
                    const currentCount = parseInt($('#watch-counter').text().match(/\d+/)[0] || '0');
                    const newCount = currentCount + 1;
                    $('#watch-counter').html(`
                        <i class="fas fa-user-friends"></i> ${newCount} ${newCount === 1 ? 'watcher' : 'watchers'}
                    `);
                }
            } else {
                alert(data.error || 'Error watching auction');
                button.prop('disabled', false);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error watching auction. Please try again.');
            button.prop('disabled', false);
        });
    }
    
    // Show the unwatch confirmation pop up
    function showUnwatchConfirmation(button, itemUrl) {
        // Create and show the modal
        if ($('#unwatchConfirmationModal').length === 0) {
            $('body').append(`
                <div class="modal fade" id="unwatchConfirmationModal" tabindex="-1" aria-labelledby="unwatchConfirmationModalLabel">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="unwatchConfirmationModalLabel">Confirm Unwatch</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p>Are you sure you want to unwatch this auction?</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-danger" id="confirm-unwatch-btn">Yes, Unwatch</button>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }
        
        const unwatchModal = new bootstrap.Modal(document.getElementById('unwatchConfirmationModal'));
        unwatchModal.show();
        
        $('#confirm-unwatch-btn').off('click').on('click', function() {
            unwatchModal.hide();
            unwatchAuction(button, itemUrl);
        });
    }
    
    function unwatchAuction(button, itemUrl) {
        // Disable button
        button.prop('disabled', true);
        
        csrfFetch(`/item/${itemUrl}/unwatch`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Replace with watch button
                const newButton = $(`
                    <button id="watch-btn" class="btn btn-outline-dark btn-lg" data-item-url="${itemUrl}">
                        <i class="fas fa-eye"></i> Add to Watchlist
                    </button>
                `);
                button.replaceWith(newButton);
                
                // Update counter if it exists
                if ($('#watch-counter').length) {
                    const currentCount = parseInt($('#watch-counter').text().match(/\d+/)[0] || '0');
                    const newCount = Math.max(0, currentCount - 1);
                    $('#watch-counter').html(`
                        <i class="fas fa-user-friends"></i> ${newCount} ${newCount === 1 ? 'watcher' : 'watchers'}
                    `);
                }
            } else {
                alert(data.error || 'Error unwatching auction');
                button.prop('disabled', false);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error unwatching auction. Please try again.');
            button.prop('disabled', false);
        });
    }
});