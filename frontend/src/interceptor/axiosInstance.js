import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
  withCredentials: true, // ✅ Позволяет передавать refresh_token из куков
});

let isRefreshing = false;
let failedRequestsQueue = [];

apiClient.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        if (!isRefreshing) {
          isRefreshing = true;

          // ✅ Обновляем токен
          const response = await apiClient.post("/auth/refresh");

          if (response.data.access_token) {
            setAccessToken(response.data.access_token);
            apiClient.defaults.headers.common["Authorization"] = `Bearer ${response.data.access_token}`;
          }

          isRefreshing = false;

          // ✅ Повторяем все запросы, которые ждали refresh
          failedRequestsQueue.forEach((req) => req.onSuccess());
          failedRequestsQueue = [];
        } else {
          return new Promise((resolve) => {
            failedRequestsQueue.push({ onSuccess: () => resolve(apiClient(originalRequest)) });
          });
        }

        return apiClient(originalRequest); // ✅ Повторяем запрос с новым токеном
      } catch (refreshError) {
        console.error("Refresh token expired. Redirecting to login...", refreshError);
        isRefreshing = false;

        // ❌ Если refresh не сработал — чистим всё и редиректим на логин
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

function setAccessToken(token) {
  localStorage.setItem("token", token);
}

function clearTokens() {
  document.cookie = "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  localStorage.removeItem("token");
}

export default apiClient;
