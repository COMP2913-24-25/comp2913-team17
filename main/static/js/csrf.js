// Global CSRF helper functions and socket

const getCSRFToken = () => {
  const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (!token) {
    console.error('CSRF token not found');
  }
  return token;
};

// Reusable fetch wrapper with CSRF
const csrfFetch = async (url, options = {}) => {
  const csrfToken = getCSRFToken();
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  };

  return fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
};

// Socket connection
window.globalSocket = io();