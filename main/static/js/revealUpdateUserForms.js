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

  // Shows the username form initially
  showForm('username');

});