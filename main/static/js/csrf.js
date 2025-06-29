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
  
  const headers = {
    'X-CSRF-Token': csrfToken
  };
  
  // Only set Content-Type to application/json if the body is not FormData
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  return fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });
};

// Socket connection
window.globalSocket = io();