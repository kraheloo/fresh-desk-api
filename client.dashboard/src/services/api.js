import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const serviceDeskApi = {
  /**
   * Get all users from ACL
   * @returns {Promise<Array>} Array of user objects with username and accessLevel
   */
  getUsers: async () => {
    const response = await apiClient.get('/api/users');
    return response.data;
  },

  /**
   * Get incident counts for a user
   * @param {string} username - The username to get metrics for
   * @param {number} days - Number of days to look back (default: 30)
   * @returns {Promise<Object>} Incident counts and metrics
   */
  getIncidentCounts: async (username, days = 30) => {
    const params = new URLSearchParams();
    if (username) {
      params.append('username', username);
    }
    params.append('days', days.toString());

    const response = await apiClient.get(`/api/data/counts?${params.toString()}`);
    return response.data;
  },
};

export default apiClient;
