import axios from "axios";

const BASE_URL = "http://127.0.0.1:6969";

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