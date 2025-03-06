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

  const socket = io();
  const url = window.location.pathname.split('/').pop();
  socket.emit('join', { auth_url: url });

  // Message form submission
  $('#message-form').on('submit', async function(e) {
    e.preventDefault();
    
    const messageText = $('#message').val().trim();
    if (!messageText) {
      return;
    }
    
    try {
      const response = await csrfFetch(`${window.location.pathname}/api/message`, {
        method: 'POST',
        body: JSON.stringify({ content: messageText })
      });
      
      const data = await response.json();
      
      if (data && data.success) {
        $('#message').val('');
      } else {
        alert('Failed to send message: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    }
  });

  // Scroll to the bottom of the messages w/ animation
  function scrollToBottom(delay) {
    $('#messages').animate({ scrollTop: $('#messages')[0].scrollHeight }, delay);
  }
  
  // Listen for new messages from SocketIO
  socket.on('new_message', function(data) {
    let messageClass = 'other-messages';
    if (data.sender_id === $('meta[name="user-id"]').attr('content')) {
      messageClass = 'my-messages';
    }
    
    const messageElement = `
      <div class="message ${messageClass}">
        <p>${data.message}</p>
        <p class="username">${data.sender} (${data.sent_at})</p>
      </div>
    `;
    $('#messages').append(messageElement);
    scrollToBottom(300);
  });

  // Check for forced reload
  socket.on('force_reload', function(data) {
    location.reload();
  });
  
  // Leave the room when the page unloads
  $(window).on('beforeunload', function() {
    socket.emit('leave', { auth_url: url });
  });

  // Scroll to bottom on page load
  scrollToBottom(0);
});