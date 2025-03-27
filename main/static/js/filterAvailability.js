document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleFilter');
    const dailyTable = document.getElementById('dailyTable');
    const weeklyTable = document.getElementById('weeklyTable');
    const dailyTbody = dailyTable.querySelector('tbody');
    const weeklyTbody = weeklyTable ? weeklyTable.querySelector('tbody') : null;
    const categoryFilter = document.getElementById('categoryFilter');
    
    // Read the current timeslot from the data attribute
    const currentSlotStr = dailyTable.getAttribute('data-current-slot');
    
    // Find the index of the current timeslot column.
    // (First header cell is "Expert", so timeslot columns start at index 1.)
    const headers = dailyTable.querySelectorAll('thead th');
    let currentIndex = -1;
    for (let i = 1; i < headers.length; i++) {
      if (headers[i].innerText.trim() === currentSlotStr) {
        currentIndex = i - 1;  // Adjust for the first cell
        break;
      }
    }
    if (currentIndex === -1) {
      console.error("Current timeslot column not found.");
    }
    
    // Global filter states
    let availableNowFilterActive = false;
    let selectedCategory = "";
    
    // Function to filter rows in the daily table
    function filterDailyRows() {
      const rows = dailyTbody.querySelectorAll('tr');
      rows.forEach(row => {
        let showRow = true;
        
        // Apply "available now" filter if active:
        if (availableNowFilterActive) {
          const cells = row.querySelectorAll('td');
          const cell = cells[currentIndex + 1]; // current timeslot cell
          if (!(cell && cell.classList.contains('bg-dark-turquoise'))) {
            showRow = false;
          }
        }
        
        // Apply category filter if one is selected:
        if (selectedCategory) {
          const rowCategories = row.getAttribute('data-categories') || "";
          const categoriesArray = rowCategories.split(',');
          if (!categoriesArray.includes(selectedCategory)) {
            showRow = false;
          }
        }
        
        row.style.display = showRow ? '' : 'none';
      });
    }
    
    // Function to filter rows in the weekly table (only category filter applies)
    function filterWeeklyRows() {
      if (!weeklyTbody) return;
      const rows = weeklyTbody.querySelectorAll('tr');
      rows.forEach(row => {
        let showRow = true;
        if (selectedCategory) {
          const rowCategories = row.getAttribute('data-categories') || "";
          const categoriesArray = rowCategories.split(',');
          if (!categoriesArray.includes(selectedCategory)) {
            showRow = false;
          }
        }
        row.style.display = showRow ? '' : 'none';
      });
    }
    
    // Toggle "available now" filter on the daily table
    toggleBtn.addEventListener('click', function() {
      availableNowFilterActive = !availableNowFilterActive;
      toggleBtn.textContent = availableNowFilterActive ? "Show All Experts" : "Show Only Currently Available Experts";
      filterDailyRows();
    });
    
    // Listen for category changes and update both tables
    if (categoryFilter) {
      categoryFilter.addEventListener('change', function() {
        selectedCategory = categoryFilter.value;
        filterDailyRows();
        filterWeeklyRows();
      });
    }
});

// Expert table filter on username search
function filterExperts() {
  const searchTerm = $('#expert-search').val().toLowerCase().trim();
  const selectedCategory = $('#categoryFilter').val(); // '' means All Categories

  $('#dailyTable tbody tr, #weeklyTable tbody tr').each(function() {
    const row = $(this);
    const username = row.find('td:first').text().toLowerCase();
    const categories = row.data('categories')?.toString().split(',') || [];

    const matchesSearch = searchTerm === '' || username.includes(searchTerm);
    const matchesCategory = selectedCategory === '' || categories.includes(selectedCategory);

    if (matchesSearch && matchesCategory) {
      row.show();
    } else {
      row.hide();
    }
  });
}

$(document).ready(function() {
  $('#expert-search').on('input', filterExperts);
  $('#categoryFilter').on('change', filterExperts);
});

