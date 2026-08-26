const RaktDaan = {
  TOKEN_KEY: 'auth_token',
  USER_KEY: 'user_data',

  getToken: () => localStorage.getItem(RaktDaan.TOKEN_KEY),
  setToken: (token) => localStorage.setItem(RaktDaan.TOKEN_KEY, token),
  
  getUser: () => {
    const data = localStorage.getItem(RaktDaan.USER_KEY);
    return data ? JSON.parse(data) : null;
  },

  setUser: (user) => {
    localStorage.setItem(RaktDaan.USER_KEY, JSON.stringify(user));
  },

  clearAuth: () => {
    localStorage.removeItem(RaktDaan.TOKEN_KEY);
    localStorage.removeItem(RaktDaan.USER_KEY);
  },

  isAuthenticated: () => !!RaktDaan.getToken(),

  apiFetch: async (endpoint, options = {}) => {
    const token = RaktDaan.getToken();
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(options.headers || {})
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(endpoint, config);
      if (response.status === 401) {
        RaktDaan.clearAuth();
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/donor/login';
        }
      }
      return response;
    } catch (err) {
      console.error('API Request Failure:', err);
      throw err;
    }
  }
};
