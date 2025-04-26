// Expert availability filter for daily and weekly tables

document.addEventListener('DOMContentLoaded', function() {
  const toggleBtn = document.getElementById('toggleFilter');
  const dailyTable = document.getElementById('dailyTable');
  const weeklyTable = document.getElementById('weeklyTable');
  const dailyTbody = dailyTable.querySelector('tbody');
  const weeklyTbody = weeklyTable ? weeklyTable.querySelector('tbody') : null;
  const categoryFilter = document.getElementById('expert-category-filter');
  const searchInput = document.getElementById('expert-search');
  const dailyTableSpacer = document.getElementById('dailyTableSpacer');
  const weeklyTableSpacer = document.getElementById('weeklyTableSpacer');
  
  // Weekly tab elements
  const weeklyTab = document.getElementById('weekly');
  const weeklyTabLink = document.getElementById('weekly-tab');
  
  // Store original table heights so we don't move footer around
  let originalDailyTableHeight = null;
  let originalWeeklyTableHeight = null;
  
  // Read the current timeslot from the data attribute
  const currentSlotStr = dailyTable.getAttribute('data-current-slot');
  
  // Find the index of the current timeslot column
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
  let searchTerm = "";
  
  // Function to calculate daily table height
  function measureDailyTableHeight() {
    if (!dailyTable) {
      return 0;
    }
    
    // Ensure all rows are visible
    const rows = dailyTbody.querySelectorAll('tr');
    const originalDisplayValues = [];
    
    // Make all rows visible
    rows.forEach(row => {
      originalDisplayValues.push(row.style.display);
      row.style.display = '';
    });
    
    // Measure the height
    const height = dailyTable.offsetHeight;
    
    // Restore original display values
    rows.forEach((row, index) => {
      row.style.display = originalDisplayValues[index];
    });

    return height;
  }
  
  // Function to calculate weekly table height when the tab is visible
  function measureWeeklyTableHeight() {
    if (!weeklyTable || !weeklyTbody) {
      return 0;
    }
    
    // If weekly tab is not visible, we need to show it for measurement
    const weeklyTabWasHidden = !weeklyTab.classList.contains('active');
    
    if (weeklyTabWasHidden) {
      // Temporarily show the weekly tab without triggering events
      weeklyTab.style.display = 'block';
      weeklyTab.style.visibility = 'visible';
      weeklyTab.style.height = 'auto';
      weeklyTab.style.overflow = 'visible';
      weeklyTab.style.opacity = '1';
    }
    
    // Ensure all rows are visible
    const rows = weeklyTbody.querySelectorAll('tr');
    const originalDisplayValues = [];
    
    // Make all rows visible
    rows.forEach(row => {
      originalDisplayValues.push(row.style.display);
      row.style.display = '';
    });
    
    // Measure the height
    const height = weeklyTable.offsetHeight;
    
    // Restore original display values
    rows.forEach((row, index) => {
      row.style.display = originalDisplayValues[index];
    });
    
    // Return the weekly tab to its original state
    if (weeklyTabWasHidden) {
      weeklyTab.style.display = '';
      weeklyTab.style.visibility = '';
      weeklyTab.style.height = '';
      weeklyTab.style.overflow = '';
      weeklyTab.style.opacity = '';
    }

    return height;
  }
  
  // Combined filter function for both tables
  function applyAllFilters() {
    filterDailyRows();
    filterWeeklyRows();
    updateSpacerHeights();
  }
  
  // Function to filter rows in the daily table
  function filterDailyRows() {
    const rows = dailyTbody.querySelectorAll('tr');
    let visibleCount = 0;
    
    // Measure daily table height if not done yet
    if (originalDailyTableHeight === null) {
      originalDailyTableHeight = measureDailyTableHeight();
    }
    
    rows.forEach(row => {
      let showRow = true;
      
      // Apply now available filter if active
      if (availableNowFilterActive) {
        const cells = row.querySelectorAll('td');
        const cell = cells[currentIndex + 1]; // current timeslot cell
        if (!(cell && cell.classList.contains('green-now'))) {
          showRow = false;
        }
      }
      
      // Apply category filter if one is selected
      if (selectedCategory) {
        const rowCategories = row.getAttribute('data-categories') || "";
        const categoriesArray = rowCategories.split(',');
        if (!categoriesArray.includes(selectedCategory)) {
          showRow = false;
        }
      }
      
      // Apply search filter if text is entered
      if (searchTerm) {
        const username = row.querySelector('td:first-child').textContent.toLowerCase();
        if (!username.includes(searchTerm.toLowerCase())) {
          showRow = false;
        }
      }
      
      row.style.display = showRow ? '' : 'none';
      if (showRow) {
        visibleCount++;
      }
    });
  }
  
  // Function to filter rows in the weekly table
  function filterWeeklyRows() {
    if (!weeklyTbody) return;
    
    // Measure weekly table height if not done yet
    if (originalWeeklyTableHeight === null) {
      originalWeeklyTableHeight = measureWeeklyTableHeight();
    }
    
    const rows = weeklyTbody.querySelectorAll('tr');
    let visibleCount = 0;
    
    rows.forEach(row => {
      let showRow = true;
      
      // Apply category filter if one is selected
      if (selectedCategory) {
        const rowCategories = row.getAttribute('data-categories') || "";
        const categoriesArray = rowCategories.split(',');
        if (!categoriesArray.includes(selectedCategory)) {
          showRow = false;
        }
      }
      
      // Apply search filter if text is entered
      if (searchTerm) {
        const username = row.querySelector('td:first-child').textContent.toLowerCase();
        if (!username.includes(searchTerm.toLowerCase())) {
          showRow = false;
        }
      }
      
      row.style.display = showRow ? '' : 'none';
      if (showRow) {
        visibleCount++;
      }
    });
  }
  
  // Function to update spacer heights
  function updateSpacerHeights() {
    if (dailyTableSpacer.style.display === 'none' || weeklyTableSpacer.style.display === 'none') {
      return;
    }

    // For daily table
    if (dailyTableSpacer && originalDailyTableHeight !== null) {
      const currentDailyTableHeight = dailyTable.offsetHeight;
      const dailySpacerHeight = Math.max(0, originalDailyTableHeight - currentDailyTableHeight);
      
      dailyTableSpacer.style.height = `${dailySpacerHeight}px`;
    }
    
    // For weekly table when weekly tab is visible
    if (weeklyTableSpacer && originalWeeklyTableHeight !== null && weeklyTab.classList.contains('active')) {
      const currentWeeklyTableHeight = weeklyTable.offsetHeight;
      const weeklySpacerHeight = Math.max(0, originalWeeklyTableHeight - currentWeeklyTableHeight);
      
      weeklyTableSpacer.style.height = `${weeklySpacerHeight}px`;
    }
  }
  
  // Toggle availability filter on the daily table
  toggleBtn.addEventListener('click', function() {
    availableNowFilterActive = !availableNowFilterActive;
    toggleBtn.textContent = availableNowFilterActive ? "Show All Experts" : "Show Only Currently Available Experts";
    applyAllFilters();
  });
  
  // Listen for category changes and update both tables
  if (categoryFilter) {
    categoryFilter.addEventListener('change', function() {
      selectedCategory = categoryFilter.value;
      applyAllFilters();
    });
  }
  
  // Listen for search input and update both tables
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      searchTerm = searchInput.value.trim();
      applyAllFilters();
    });
  }
  
  // Handle tab switching
  const tabLinks = document.querySelectorAll('a[data-bs-toggle="tab"]');
  tabLinks.forEach(tab => {
    tab.addEventListener('shown.bs.tab', function(e) {
      // If switching to weekly tab and we haven't measured it yet, measure it
      if (e.target.id === 'weekly-tab' && originalWeeklyTableHeight === null) {
        originalWeeklyTableHeight = measureWeeklyTableHeight();
      }
      
      // Update spacers after tab switch
      setTimeout(updateSpacerHeights, 50);
    });
  });
  
  // Update on window resize
  window.addEventListener('resize', function() {
    // Re-measure heights on resize
    originalDailyTableHeight = measureDailyTableHeight();
    if (weeklyTab.classList.contains('active') || originalWeeklyTableHeight !== null) {
      originalWeeklyTableHeight = measureWeeklyTableHeight();
    }
    updateSpacerHeights();
  });
  
  // Initialise once the page is fully loaded
  window.addEventListener('load', function() {
    // Measure the daily table
    originalDailyTableHeight = measureDailyTableHeight();
    
    // Measure the weekly table if it's visible and we haven't done so yet
    if (weeklyTabLink) {
      weeklyTabLink.addEventListener('click', function() {
        if (originalWeeklyTableHeight === null) {
          // Small delay to ensure the tab is fully visible
          setTimeout(function() {
            originalWeeklyTableHeight = measureWeeklyTableHeight();
            updateSpacerHeights();
          }, 100);
        }
      });
    }
    applyAllFilters();
  });
});