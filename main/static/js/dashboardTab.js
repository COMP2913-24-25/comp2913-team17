// Remembers the auction tab that the user was on when they last visited the dashboard

$(document).ready(function() {
  $(function() {
    if ($('#participatedTabs').length) {
      $('#participatedTabs .nav-link').on('shown.bs.tab', function(e) {
        // Save the active tab ID to sessionStorage
        const tabId = $(this).attr('id');
        sessionStorage.setItem('activeAuctionTab', tabId);
      });
      
      // Check if we have a saved tab
      const savedTab = sessionStorage.getItem('activeAuctionTab');
      
      if (savedTab) {
        const currTab = $('#' + savedTab);
        
        if (currTab.length) {
          currTab.tab('show');
        }
      }
    }
  });
});