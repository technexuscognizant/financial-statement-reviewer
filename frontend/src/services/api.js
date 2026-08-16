import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const uploadFinancialFile = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  return API.post("/api/analyze", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export default API;