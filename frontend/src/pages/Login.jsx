import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/login.scss";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError("");

    const formData = new URLSearchParams(); // ✅ Используем URLSearchParams
    formData.append("username", email); // ✅ FastAPI требует "username", не "email"
    formData.append("password", password);
    formData.append("grant_type", "password");

    try {
      const response = await axios.post("http://127.0.0.1:8000/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded", // ✅ Правильный заголовок
        },
      });

      localStorage.setItem("token", response.data.access_token);
      navigate("/chat");
    } catch (err) {
      console.error("Ошибка при входе:", err);
      setError("Неверный email или пароль.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Sign In</h1>
        {error && <p className="error">{error}</p>} {/* ✅ Показываем ошибку */}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button onClick={handleLogin}>Sign In</button>
      </div>
    </div>
  );
}
