// Scripts for the item authentication page

$(document).ready(function() {
  // Expert item authentication button
  $('#authenticate-item').on('click', async function() {
    if (!confirm('Are you sure you want to authenticate this item?\nThis action cannot be undone.')) {
      return;
    }

    try {
      const response = await csrfFetch(`${window.location.pathname}/api/accept`, {
        method: 'POST'
      });
          
      const data = await response.json();
      
      if (data && data.success) {
        alert('Item authenticated successfully!');
        window.location = $('#item-link').attr('href');
      } else {
        alert('Failed to authenticate item.');
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });

  // Expert item authentication rejection button
  $('#decline-item').on('click', async function() {
    if (!confirm('Are you sure you want to decline this item?\nThis action cannot be undone.')) {
      return;
    }

    try {
      const response = await csrfFetch(`${window.location.pathname}/api/decline`, {
        method: 'POST'
      });
          
      const data = await response.json();
      
      if (data && data.success) {
        alert('Item declined successfully!');
        window.location = $('#item-link').attr('href');
      } else {
        alert('Failed to decline item.');
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });

  // Expert item reassignment button
  $('#reassign-item').on('click', async function() {
    if (!confirm('Are you sure you want to reassign this item?\nThis action cannot be undone.')) {
      return;
    }

    try {
      const response = await csrfFetch(`${window.location.pathname}/api/reassign`, {
        method: 'POST'
      });
          
      const data = await response.json();
      
      if (data && data.success) {
        alert('Item scheduled for reassignment!');
        window.location = $('#item-link').attr('href');
      } else {
        alert('Failed to reassign item.');
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });

  const url = window.location.pathname.split('/').pop();
  window.globalSocket.emit('join_chat', { auth_url: url });

  // Handle file selection display
  $('#images').on('change', function() {
    const files = this.files;
    const MAX_IMAGES = 5;
    const MAX_FILE_SIZE = 1024 * 1024;
    let selectedFilesHtml = '';
    let errorMessages = [];
    
    // Check if too many files selected
    if (files.length > MAX_IMAGES) {
      errorMessages.push(`Maximum ${MAX_IMAGES} images allowed.`);
      // Clear selection
      $(this).val('');
      $('#selected-files').html(`<div class="error">${errorMessages.join('<br>')}</div>`);
      return;
    }
    
    // Validate each file
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        errorMessages.push(`${file.name} exceeds maximum size of 1MB.`);
        continue;
      }
      
      // Check file type
      const fileExt = file.name.split('.').pop().toLowerCase();
      if (!['jpg', 'jpeg', 'png'].includes(fileExt)) {
        errorMessages.push(`${file.name} is not an allowed file type.`);
        continue;
      }
      
      selectedFilesHtml += `<div class="selected-file">${file.name}</div>`;
    }
    
    // Display errors or selected files
    if (errorMessages.length > 0) {
      // Clear selection if any errors
      $(this).val('');
      $('#selected-files').html(`<div class="error">${errorMessages.join('<br>')}</div>`);
    } else {
      $('#selected-files').html(selectedFilesHtml);
    }
  });

  // Message form submission
  $('#message-form').on('submit', async function(e) {
    e.preventDefault();
    
    const messageText = $('#message').val().trim();
    const files = $('#images')[0].files;
    if (!messageText) {
        alert('Message cannot be empty');
        return;
    }

    // Validate number of files
    const MAX_IMAGES = 5;
    const MAX_FILE_SIZE = 1024 * 1024;
    
    if (files.length > MAX_IMAGES) {
      alert(`Maximum ${MAX_IMAGES} images allowed.`);
      return;
    }

    // Validate each file size
    for (let i = 0; i < files.length; i++) {
      if (files[i].size > MAX_FILE_SIZE) {
        alert(`File "${files[i].name}" exceeds maximum size of 1MB.`);
        return;
      }
    }

    // Add loading indicator
    const sendButton = $(this).find('button[type="submit"]');
    const originalText = sendButton.text();
    sendButton.prop('disabled', true).text('Sending...');

    const formData = new FormData();
    formData.append('content', messageText);

    // Append all files to formData
    for (let i = 0; i < files.length; i++) {
      formData.append('files[]', files[i]);
    }

    // Add temporary message indicator
    let tempMessageHtml = `
    <div class="message my-messages temp-message">
      <p>${messageText}</p>`;

    if (files.length > 0) {
    tempMessageHtml += `<p class="username">Uploading ${files.length} image${files.length > 1 ? 's' : ''}...</p>`;
    } else {
    tempMessageHtml += `<p class="username">Sending...</p>`;
    }
    tempMessageHtml += `</div>`;

    $('#messages').append(tempMessageHtml);
    scrollToBottom(300);

    try {
      const response = await csrfFetch(`${window.location.pathname}/api/message`, {
        method: 'POST',
        body: formData
      });
        
      const data = await response.json();
        
      if (data && data.success) {
        $('#message').val('');
        $('#images').val('');
        $('#selected-files').html('');
        $('.temp-message').remove();
      } else {
        alert('Failed to send message: ' + (data.error || 'Unknown error'));
        $('.temp-message').remove();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
      $('.temp-message').remove();
    } finally {
      sendButton.prop('disabled', false).text(originalText);
    }
  });

  // Scroll to the bottom of the messages w/ animation
  function scrollToBottom(delay) {
    $('#messages').animate({ scrollTop: $('#messages')[0].scrollHeight }, delay);
  }
  
  // Listen for new messages from window.globalSocketIO
  window.globalSocket.on('new_message', function(data) {
    let messageClass = 'other-messages';
    if (data.sender_id === $('meta[name="user-id"]').attr('content')) {
      messageClass = 'my-messages';
    }

    let imagesHtml = '';
    if (data.images && data.images.length > 0) {
      imagesHtml = '<div class="image-gallery">';
      for (let i = 0; i < data.images.length; i++) {
        imagesHtml += `<a href="${data.images[i]}" target="_blank">
          <img src="${data.images[i]}" class="message-image" alt="Attached image">
        </a>`;
      }
      imagesHtml += '</div>';
    }
    
    const messageElement = `
      <div class="message ${messageClass}">
        <p>${data.message}</p>
        ${imagesHtml}
        <p class="username">${data.sender} (${data.sent_at})</p>
      </div>
    `;
    $('#messages').append(messageElement);
    scrollToBottom(300);
  });

  // Check for forced reload
  window.globalSocket.on('force_reload', function(data) {
    location.reload();
  });
  
  // Leave the room when the page unloads
  $(window).on('beforeunload', function() {
    window.globalSocket.emit('leave', { 'auth_url': url });
  });
});