import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL;

export const sendMessage = async (message, threadId = null) => {
  const response = await axios.post(`${BASE_URL}/chat`, {
    message,
    thread_id: threadId,
  });

  return response.data;
};

export const resumeChat = async (threadId, answer) => {
  const response = await axios.post(`${BASE_URL}/resume`, {
    thread_id: threadId,
    answer,
  });

  return response.data;
};

export const fetchMessages = async (threadId, page = 1, page_size = 15) => {
    if(!threadId) return [];
    try {
        const response = await axios.get(`${BASE_URL}/history/${threadId}`, {
            params: { page, page_size }
        });
        // console.log("Fetched messages:", response.data);
        return response.data || [];
    }
    catch(err) {
        console.error("Failed to fetch messages:", err);
        return [];
    }
};

export const fetchTables = async (threadId) => {
  try {
    const response = await axios.get(`${BASE_URL}/tables/${threadId}`);
    return response.data.tables || [];
  }
  catch(err) {
    console.error("Failed to fetch tables:", err);
    return [];
  };
}

export const fetchTableData = async (threadId, tableName) => {
  try {
    const response = await axios.get(`${BASE_URL}/tables/${threadId}/${tableName}`);
    return response.data || [];
  }
  catch(err) {
    console.error("Failed to fetch tables:", err);
    return [];
  };
}