import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/auth.scss"; // Подключаем стили

export default function Register() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setError("Пароли не совпадают!");
            return;
        }

        try {
            const response = await axios.post("http://localhost:8000/register", {
                email,
                password,
            });

            if (response.status === 201) {
                navigate("/login"); // Перенаправляем на страницу входа после успешной регистрации
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Ошибка регистрации");
        }
    };

    return (
        <div className="auth-container">
            <h2>Регистрация</h2>
            <form onSubmit={handleRegister}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Пароль"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Повторите пароль"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                {error && <p className="error">{error}</p>}
                <button type="submit">Зарегистрироваться</button>
            </form>
            <p>
                Уже есть аккаунт? <a href="/login">Войти</a>
            </p>
        </div>
    );
}
