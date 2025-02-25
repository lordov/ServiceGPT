import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/auth.scss"; // Подключаем стили

export default function Register() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();

    // ✅ Регистрация нового пользователя
    const handleRegister = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setError("Пароли не совпадают!");
            return;
        }

        try {
            await axios.post("http://localhost:8000/auth/register", {
                email,
                password,
            });
            setSuccess(true); // Показываем сообщение об успешной регистрации
            setEmail("");
            setPassword("");
            setConfirmPassword("");
        } catch (err) {
            setError("Ошибка при регистрации. Возможно, email уже используется.");
        }
    };

    // 🔄 Редирект на страницу логина через 3 секунды
    useEffect(() => {
        if (success) {
            const timer = setTimeout(() => {
                navigate("/login");
            }, 3000);

            return () => clearTimeout(timer); // Очистка таймера при размонтировании
        }
    }, [success, navigate]);

    return (
        <div className="auth-container">
            {!success ? (
                <>
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
                </>
            ) : (
                <div className="success-message">
                    <h2>🎉 Регистрация прошла успешно!</h2>
                    <p>Вы будете перенаправлены на страницу входа через несколько секунд...</p>
                </div>
            )}
        </div>
    );
}
