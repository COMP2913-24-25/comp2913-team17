// Remembers the tabs the user was on in the dashboard in session storage

$(document).ready(function() {
  // Function to restore bidding subtab
  function restoreBiddingSubTab() {
    const activeBiddingSubTabId = sessionStorage.getItem('biddingSubTabActiveTab');

    if (activeBiddingSubTabId) {
      const activeBiddingSubTab = document.getElementById(activeBiddingSubTabId);

      if (activeBiddingSubTab) {
        const biddingSubTab = new bootstrap.Tab(activeBiddingSubTab);
        biddingSubTab.show();
      }
    }
  }

  // Expert dashboard tabs
  const expertiseTabs = document.querySelectorAll('#expertDashboardTabs .nav-link');
  
  // Click handler to each tab
  expertiseTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      sessionStorage.setItem('expertDashboardActiveTab', this.id);
    });
  });
  
  const activeExpertTabId = sessionStorage.getItem('expertDashboardActiveTab');

  if (activeExpertTabId) {
    const activeExpertTab = document.getElementById(activeExpertTabId);

    if (activeExpertTab) {
      const expertTab = new bootstrap.Tab(activeExpertTab);
      expertTab.show();
    }
  }

  // Manager dashboard tabs
  const managerTabs = document.querySelectorAll('#managerDashboardTabs .nav-link');
  
  // Click handler to each tab
  managerTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      sessionStorage.setItem('managerDashboardActiveTab', this.id);
    });
  });
  
  const activeManagerTabId = sessionStorage.getItem('managerDashboardActiveTab');

  if (activeManagerTabId) {
    const activeManagerTab = document.getElementById(activeManagerTabId);

    if (activeManagerTab) {
      const managerTab = new bootstrap.Tab(activeManagerTab);
      managerTab.show();
    }
  }

  // User dashboard tabs
  const userTabs = document.querySelectorAll('#userDashboardTabs .nav-link');
  
  // Click handler to each tab
  userTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      sessionStorage.setItem('userDashboardActiveTab', this.id);
      
      // If switching to bidding tab, restore the bidding subtab
      if (this.id === 'bidding-tab') {
        restoreBiddingSubTab();
      }
    });
  });
  
  const activeUserTabId = sessionStorage.getItem('userDashboardActiveTab');

  if (activeUserTabId) {
    const activeUserTab = document.getElementById(activeUserTabId);

    if (activeUserTab) {
      const userTab = new bootstrap.Tab(activeUserTab);
      userTab.show();
    
      // If the active tab is bidding, also restore the bidding subtab
      if (activeUserTabId === 'bidding-tab') {
        restoreBiddingSubTab();
      }
    }
  }
  
  // Bidding subtabs
  const biddingSubTabs = document.querySelectorAll('#biddingSubTabs .nav-link');
  
  // Click handler to each bidding subtab
  biddingSubTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      sessionStorage.setItem('biddingSubTabActiveTab', this.id);
    });
  });
  
  // Check for payment status in URL and switch to the proper tab if needed
  const urlParams = new URLSearchParams(window.location.search);
  const paymentStatus = urlParams.get('payment_status');
  
  if (paymentStatus) {
    // Activate the bidding tab and won subtab
    const biddingTab = document.getElementById('bidding-tab');
    if (biddingTab) {
      const biddingTabInstance = new bootstrap.Tab(biddingTab);
      biddingTabInstance.show();
      
      // Small delay to ensure tab switching works
      setTimeout(() => {
        const wonTab = document.getElementById('won-tab');
        if (wonTab) {
          const wonTabInstance = new bootstrap.Tab(wonTab);
          wonTabInstance.show();
        }
      }, 100);
    }
    
    // Clean URL after displaying alerts
    const url = new URL(window.location);
    url.searchParams.delete('payment_status');
    // Use replaceState to not affect browser history
    window.setTimeout(() => {
      window.history.replaceState({}, '', url);
    }, 300);
  }
});