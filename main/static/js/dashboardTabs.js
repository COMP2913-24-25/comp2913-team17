// Remembers the tabs the user was on in the dashboard

$(document).ready(function() {
  $(function() {
    // Expert dashboard tabs
    const expertiseTabs = document.querySelectorAll('#expertDashboardTabs .nav-link');
    
    // Add click handler to each tab
    expertiseTabs.forEach(tab => {
      tab.addEventListener('click', function() {
        sessionStorage.setItem('expertDashboardActiveTab', this.id);
      });
    });
    
    const activeTabId = sessionStorage.getItem('expertDashboardActiveTab');
    if (activeTabId) {
      const activeTab = document.getElementById(activeTabId);
      if (activeTab) {
        const tab = new bootstrap.Tab(activeTab);
        tab.show();
      }
    }

    // User auction tabs
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