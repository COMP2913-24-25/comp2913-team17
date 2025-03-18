document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const dailyTable = document.getElementById('dailyTable');
    const tbody = dailyTable.querySelector('tbody');
    
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
    
    let filterOn = false;
    toggleBtn.addEventListener('click', function() {
      const rows = tbody.querySelectorAll('tr');
      if (!filterOn) {
        // Hide rows where the cell in the current timeslot column does NOT have class "bg-dark-turquoise"
        rows.forEach(row => {
          const cells = row.querySelectorAll('td');
          // Since the first cell is expert name, our timeslot cells start at index 1,
          // so the current timeslot cell is at index currentIndex + 1.
          const cell = cells[currentIndex + 1];
          if (cell && !cell.classList.contains('bg-dark-turquoise')) {
            row.style.display = 'none';
          }
        });
        toggleBtn.textContent = "Show All Experts";
        filterOn = true;
      } else {
        // Show all rows
        rows.forEach(row => {
          row.style.display = '';
        });
        toggleBtn.textContent = "Show Only Currently Available Experts";
        filterOn = false;
      }
    });

        categoryFilter.addEventListener('change', function() {
        let category = categoryFilter.value;

        fetch(`/manager/filter-experts?category_id=${category}`)
            .then(response => response.json())
            .then(data => {
                console.log("API response:", data);
                
                tbody.innerHTML = ""; // Clear current table rows

                data.forEach(expert => {
                    let row = document.createElement("tr");
                    let nameCell = document.createElement("td");
                    nameCell.textContent = expert.username;
                    row.appendChild(nameCell);

                    // Add empty cells for each time slot
                    let numColumns = document.querySelector("#dailyTable thead tr").children.length - 1;
                    for (let i = 0; i < numColumns; i++) {
                        let emptyCell = document.createElement("td");
                        emptyCell.textContent = "-";
                        row.appendChild(emptyCell);
                    }

                    tbody.appendChild(row);
                });

                // Ensure toggle filter is reset when new data is loaded
                filterOn = false;
                toggleBtn.textContent = "Show Only Currently Available Experts";
            })
            .catch(error => console.error("Error fetching experts:", error));
    });

    categoryFilter.addEventListener('change', function() {
      let category = categoryFilter.value;

      fetch(`/manager/filter-experts?category_id=${category}`)
          .then(response => response.json())
          .then(data => {
              tbody.innerHTML = ""; // Clear current table rows

              data.forEach(expert => {
                  let row = document.createElement("tr");
                  let nameCell = document.createElement("td");
                  nameCell.textContent = expert.username;
                  row.appendChild(nameCell);

                  // Add empty cells for each time slot
                  let numColumns = document.querySelector("#dailyTable thead tr").children.length - 1;
                  for (let i = 0; i < numColumns; i++) {
                      let emptyCell = document.createElement("td");
                      emptyCell.textContent = "-";
                      row.appendChild(emptyCell);
                  }

                  tbody.appendChild(row);
              });

              // Ensure toggle filter is reset when new data is loaded
              filterOn = false;
              toggleBtn.textContent = "Show Only Currently Available Experts";
          })
          .catch(error => console.error("Error fetching experts:", error));
    });
  });