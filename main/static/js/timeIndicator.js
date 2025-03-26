document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('dailyTableContainer');
    const table = document.getElementById('dailyTable');
    const indicator = document.getElementById('currentTimeIndicator');
    
    if (container && table && indicator) {
      // Get header cells (the first row of the table head)
      const headerCells = table.querySelectorAll('thead th');
      const currentSlotStr = table.getAttribute('data-current-slot');
      let currentSlotIndex = -1;
      
      // The first header cell is "Expert"; timeslot cells start at index 1.
      for (let i = 1; i < headerCells.length; i++) {
        if (headerCells[i].innerText.trim() === currentSlotStr) {
          currentSlotIndex = i - 1;  // Now timeslot index (0-based for timeslot columns)
          break;
        }
      }
      
      if (currentSlotIndex !== -1) {
        // Compute the horizontal (left) position based on the header cell.
        const timeslotHeaderCell = headerCells[currentSlotIndex + 1];
        const headerRect = timeslotHeaderCell.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        const offsetLeft = headerRect.left - containerRect.left;
        const centerOffset = offsetLeft + (headerRect.width / 2) - (indicator.offsetWidth / 2);
        indicator.style.left = `${centerOffset}px`;
        
        // Now, limit the vertical span to only the "Now" cells.
        // Get all rows in the tbody.
        const rows = table.querySelectorAll('tbody tr');
        if (rows.length > 0) {
          // In each row, the first cell is "Expert", so timeslot cells start at index 1.
          const cellIndex = currentSlotIndex + 1;
          const firstCell = rows[0].children[cellIndex];
          const lastCell = rows[rows.length - 1].children[cellIndex];
          const firstCellRect = firstCell.getBoundingClientRect();
          const lastCellRect = lastCell.getBoundingClientRect();
          
          // Calculate the top offset and the height relative to the container.
          const topOffset = firstCellRect.top - containerRect.top;
          const bottom = lastCellRect.bottom - containerRect.top;
          const height = bottom - topOffset;
          indicator.style.top = `${topOffset}px`;
          indicator.style.height = `${height}px`;
        }
      }
    }
  });
  