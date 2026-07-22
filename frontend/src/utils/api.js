import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const uploadImages = async (files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 30000, // 30 second timeout
  });
  
  return response.data;
};

export const checkJobStatus = async (jobId) => {
  const response = await axios.get(`${API_BASE_URL}/status/${jobId}`);
  return response.data;
};

// Mock payment trigger
export const triggerPremiumUpgrade = async (jobId) => {
  // Mocking the stripe webhook call directly for development purposes
  const response = await axios.post(`${API_BASE_URL}/webhook`, {
    job_id: jobId,
    status: 'paid'
  });
  return response.data;
};
