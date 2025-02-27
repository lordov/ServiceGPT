import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

let isRefreshing = false;
let failedRequestsQueue = [];

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        if (!isRefreshing) {
          isRefreshing = true;

          // Обновляем Access Token через Refresh Token
          const response = await apiClient.post("/auth/refresh", {
            refresh_token: getRefreshTokenFromCookie(),
          });

          if (response.data.access_token) {
            setAccessTokenInStorage(response.data.access_token);
            apiClient.defaults.headers.common[
              "Authorization"
            ] = `Bearer ${response.data.access_token}`;
          }

          isRefreshing = false;

          // Повторяем все запросы из очереди
          failedRequestsQueue.forEach((req) => req.onSuccess());
          failedRequestsQueue = [];
        } else {
          return new Promise((resolve) => {
            failedRequestsQueue.push({ onSuccess: () => resolve(apiClient(originalRequest)) });
          });
        }

        return apiClient(originalRequest); // Повторяем оригинальный запрос
      } catch (refreshError) {
        console.error("Failed to refresh token", refreshError);
        isRefreshing = false;

        // Очищаем токены и перенаправляем пользователя на страницу входа
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

function getRefreshTokenFromCookie() {
  const cookies = document.cookie.split("; ").find((row) => row.startsWith("refresh_token="));
  return cookies ? cookies.split("=")[1] : null;
}

function setAccessTokenInStorage(token) {
  localStorage.setItem("access_token", token);
}

function clearTokens() {
  document.cookie = "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  localStorage.removeItem("access_token");
}

export default apiClient;