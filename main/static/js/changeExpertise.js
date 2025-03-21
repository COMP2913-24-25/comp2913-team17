// Allows experts to modify their expertise

$(document).ready(function() {
  const userID = $('meta[name="user-id"]').attr('content');

  if (!userID) {
    return;
  }

  // Function to update the Current Expertise display
  function updateCurrentExpertiseDisplay(expertiseIds) {
    const currentExpertiseDiv = $('#current-expertise');
    currentExpertiseDiv.empty();
    
    if (expertiseIds.length === 0) {
      currentExpertiseDiv.html('<p class="text-muted mono text-center my-1">No areas of expertise selected yet.</p>');
      return;
    }
    
    // For each checked expertise, create a badge with name and description
    expertiseIds.forEach(id => {
      const checkbox = $(`input[value="${id}"]`);
      if (checkbox.length) {
        const name = checkbox.next('label').text().trim();
        const description = checkbox.next('label').attr('title') || '';
        
        currentExpertiseDiv.append(`
          <span class="badge expertise-badge" title="${description}">${name}</span>
        `);
      }
    });
  }

  // Store the initial state of checkboxes for the cancel action
  let initialState = {};
  $('input[name="expertise"]').each(function() {
    const categoryId = $(this).val();
    initialState[categoryId] = $(this).prop('checked');
  });
  
  // Asynchronously update the expertise list
  $('#expertise-form').on('submit', async function(e) {
    e.preventDefault();

    // Show loading state
    const submitBtn = $(this).find('button[type="submit"]');
    const originalText = submitBtn.text();
    
    // Get all selected category IDs
    const selectedExpertise = [];
    $('input[name="expertise"]:checked').each(function() {
      selectedExpertise.push(parseInt($(this).val(), 10));
    });

    try {
      const response = await csrfFetch(`/dashboard/api/expert/${userID}`, {
        method: 'PUT',
        body: JSON.stringify({ expertise: selectedExpertise })
      });
          
      const data = await response.json();
      
      if (data && data.message) {
        // Get the updated expertise list from the response
        const updatedExpertise = data.expertise || [];
        updateCurrentExpertiseDisplay(updatedExpertise);
        
        // Change the initial state to reflect the new changes
        initialState = {};

        $('input[name="expertise"]').each(function() {
          const categoryId = parseInt($(this).val(), 10);

          // Set checked state based on the updated expertise list
          const isChecked = updatedExpertise.includes(categoryId);
          $(this).prop('checked', isChecked);
          initialState[categoryId] = isChecked;
        });
      }
    } catch (error) {
      console.log('Error:', error);
    }
  });
  
  // Select all button
  $('#select-all').click(function() {
    $('input[name="expertise"]').prop('checked', true);
  });
  
  // Deselect all button
  $('#deselect-all').click(function() {
    $('input[name="expertise"]').prop('checked', false);
  });
  
  // Cancel button - reset to original state based on the updated initial state
  $('#cancel-changes').click(function() {
    for (const [categoryId, isChecked] of Object.entries(initialState)) {
      $(`input[value="${categoryId}"]`).prop('checked', isChecked);
    }
  });
});
