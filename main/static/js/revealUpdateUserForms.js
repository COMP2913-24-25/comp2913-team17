// Script for the user update forms

$(document).ready(function() {
  function showForm(formId) {
    // When the document is loaded, hide all the forms
    $('#username-form').hide();
    $('#email-form').hide();
    $('#password-form').hide();
    
    // Show the form that has been clicked
    $('#' + formId + '-form').show();
    
    // Clears the highlighted list items
    $('#username-link').removeClass('active');
    $('#email-link').removeClass('active');
    $('#password-link').removeClass('active');
    
    // Highlights only the selected form link
    $('#' + formId + '-link').addClass('active');

    // Keeps track of the form that the user used
    localStorage.setItem('activeForm', formId);

    // Flushes the data from the hidden forms
    if (formId != 'username') {
      $('#update-username-form')[0].reset();
      $('#update-username-form .alert.alert-danger').remove();
    }
    if (formId != 'email') {
        $('#update-email-form')[0].reset();
        $('#update-email-form .alert.alert-danger').remove();
    }
    if (formId != 'password') {
        $('#update-password-form')[0].reset();
        $('#update-password-form .alert.alert-danger').remove();
    }
  }

  // Attach click events to each list item
  $('#username-link').on('click', function() {
    showForm('username');
  });
  
  $('#email-link').on('click', function() {
    showForm('email');
  });
  
  $('#password-link').on('click', function() {
    showForm('password');
  });

  // Render the form the user was last on, or username by default
  let form = localStorage.getItem('activeForm') || 'username';
  showForm(form)
});