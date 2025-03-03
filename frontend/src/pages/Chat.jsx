// import Navbar from "../components/Navbar";
import ChatSidebar from "../components/ChatSidebar";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { motion } from "framer-motion";
import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../interceptor/axiosInstance";
import "../styles/chat.scss";

export default function Chat() {
    const [chats, setChats] = useState([]); // Список чатов
    const [selectedChat, setSelectedChat] = useState(null); // Выбранный чат
    const [messages, setMessages] = useState([]); // Сообщения чата
    const [input, setInput] = useState(""); // Поле ввода
    const navigate = useNavigate();
    const messagesEndRef = useRef(null);
    const [error, setError] = useState(""); // Ошибки
    const token = localStorage.getItem("token");
    const [copied, setCopied] = useState(false);
    const [isLoading, setIsLoading] = useState(false); // ✅ Индикатор загрузки


    const messageVariants = {
        hidden: { opacity: 0, y: 10 },
        visible: { opacity: 1, y: 0 },
    };

    const handleCopy = async (code) => {
        try {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500); // ✅ Через 1.5 секунды сбрасываем статус
        } catch (err) {
            console.error("Ошибка при копировании:", err);
        }
    };

    // 📌 Функция авто-скролла
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // 📌 Скроллим вниз при изменении списка сообщений
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // 📌 Загружаем список чатов
    useEffect(() => {
        const fetchChats = async () => {
            try {
                if (!token) {
                    navigate("/login");
                    return;
                }

                const response = await apiClient.get("http://localhost:8000/chats", {
                    headers: { Authorization: `Bearer ${token}` },
                });

                setChats(response.data);
            } catch (error) {
                console.error("Ошибка при загрузке чатов:", error);
                navigate("/login");
            }
        };

        fetchChats();
    }, [navigate, token]);

    // 📌 Загружаем сообщения чата
    const fetchMessages = async (chatId) => {
        try {
            const response = await apiClient.get(`http://localhost:8000/chats/${chatId}/messages`, {
                headers: { Authorization: `Bearer ${token}` },
            });

            setMessages(response.data);
            setSelectedChat(chatId);
            navigate(`/chat/${chatId}`);
        } catch (error) {
            console.error("Ошибка при загрузке сообщений:", error);
        }
    };

    const handleDeleteChat = async (chatId) => {
        try {
            await apiClient.delete(`http://localhost:8000/chats/${chatId}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            // Обновляем список чатов, исключая удалённый
            setChats(prevChats => prevChats.filter(chat => chat.id !== chatId));

            // Если удалённый чат был выбран, сбрасываем его
            if (selectedChat === chatId) {
                setSelectedChat(null);
                setMessages([]);
            }
        } catch (error) {
            console.error("Ошибка при удалении чата", error);
        }
    };

    // 📌 Отправка сообщения
    const sendMessage = async () => {
        if (!input.trim()) return;

        // Сохраняем текст сообщения пользователя
        const userMessage = {
            content: input,
        };

        // Добавляем сообщение пользователя в список сразу (оптимистичное обновление)
        setMessages(prevMessages => [...prevMessages, userMessage]);

        setIsLoading(true);
        const messageContent = input;
        setInput("");

        try {
            let response;
            if (selectedChat) {
                // Отправляем сообщение в существующий чат
                response = await apiClient.post(
                    `http://localhost:8000/chats/${selectedChat}/messages`,
                    { content: messageContent },
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                // Добавляем ответ бота к списку сообщений
                setMessages(prevMessages => [...prevMessages, response.data]);
            } else {
                // Создаём новый чат и отправляем первое сообщение
                response = await apiClient.post(
                    "http://localhost:8000/chats/messages",
                    { content: messageContent },
                    { headers: { Authorization: `Bearer ${token}` } }
                );

                setSelectedChat(response.data.chat_id);

                // Обновляем список чатов (если необходимо)
                const chatsResponse = await apiClient.get("http://localhost:8000/chats", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setChats(chatsResponse.data);

                // Получаем сообщения нового чата и обновляем state
                const messagesResponse = await apiClient.get(`http://localhost:8000/chats/${response.data.chat_id}/messages`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setMessages(messagesResponse.data);
            }
            setError("");
        } catch (error) {
            console.error("Ошибка при отправке сообщения:", error);
            setError("Не удалось отправить сообщение.");
            // При ошибке можно, например, удалить оптимистично добавленное сообщение или пометить его как неотправленное
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <div className="chat-container">
                {/* 📌 Боковая панель с чатами */}
                <ChatSidebar
                    chats={chats}
                    selectedChat={selectedChat}
                    onSelectChat={fetchMessages}
                    onNewChat={() => setSelectedChat(null)}
                    onDeleteChat={handleDeleteChat}
                />
                {/* 📌 Основное окно чата */}
                <div className="chat-main">
                    {selectedChat ? (
                        <>
                            <div className="chat-messages">
                                {messages.map((msg, index) => (
                                    <motion.div
                                        key={index}
                                        className={`chat-message ${msg.sender_id === 1 ? "bot" : "user"}`}
                                        initial="hidden"
                                        animate="visible"
                                        variants={messageVariants}
                                    >
                                        <ReactMarkdown
                                            components={{
                                                code({ node, inline, className, children, ...props }) {
                                                    const match = /language-(\w+)/.exec(className || "");
                                                    const codeText = String(children).replace(/\n$/, "");

                                                    return !inline && match ? (
                                                        <div style={{ position: "relative" }}>
                                                            <button
                                                                onClick={() => handleCopy(codeText)}
                                                                style={{
                                                                    position: "absolute",
                                                                    right: "10px",
                                                                    top: "10px",
                                                                    background: copied ? "green" : "rgba(255,255,255,0.2)",
                                                                    color: "#fff",
                                                                    border: "none",
                                                                    padding: "5px 10px",
                                                                    cursor: "pointer",
                                                                    borderRadius: "5px",
                                                                    fontSize: "12px",
                                                                }}
                                                            >
                                                                {copied ? "Скопировано!" : "Копировать"}
                                                            </button>

                                                            <SyntaxHighlighter
                                                                style={atomDark}
                                                                language={match[1]}
                                                                PreTag="div"
                                                                {...props}
                                                            >
                                                                {codeText}
                                                            </SyntaxHighlighter>
                                                        </div>
                                                    ) : (
                                                        <code className={className} {...props}>
                                                            {children}
                                                        </code>
                                                    );
                                                },
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </motion.div>
                                ))}
                                {/* ✅ Показываем индикатор загрузки, если идет запрос */}
                                {isLoading && (
                                    <div className="loading-indicator">
                                        <span className="dot"></span>
                                        <span className="dot"></span>
                                        <span className="dot"></span>
                                    </div>
                                )}
                                <div ref={messagesEndRef} /> {/* 📌 Прокрутка вниз */}
                            </div>
                        </>
                    ) : (
                        <div className="chat-placeholder">Введите сообщение, чтобы начать новый чат</div>
                    )}

                    <div className="chat-input">
                        <input
                            type="text"
                            placeholder="Введите сообщение..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey && !isLoading) {
                                    e.preventDefault(); // Отменяем перенос строки
                                    sendMessage();
                                }
                            }}
                            disbled={isLoading}
                        />
                        {/* ✅ Показываем индикатор загрузки вместо кнопки */}
                        {isLoading ? (
                            <div className="loading-spinner"></div>
                        ) : (
                            <button onClick={sendMessage}>➤</button>
                        )}
                        {error && <div className="error">{error}</div>} {/* ✅ Показываем ошибку */}
                    </div>
                </div>
            </div>
        </>
    );
}
