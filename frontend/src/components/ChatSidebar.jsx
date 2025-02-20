import { useNavigate } from "react-router-dom";

export default function ChatSidebar({ chats, selectedChat, onSelectChat, onNewChat }) {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/login");
    };

    return (
        <div className="chat-sidebar">
            {/* 📌 Верхняя часть (лого + кнопка нового чата) */}
            <div className="sidebar-header">
                <img src="/logo.png" alt="Logo" className="logo" />
                <h1>ServiceGPT</h1>
            </div>
            <button className="new-chat-btn" onClick={onNewChat}>Новый чат</button>

            {/* 📌 Список чатов */}
            <h2>Чаты</h2>
            <ul>
                {chats.map((chat) => (
                    <li key={chat.id}
                        className={selectedChat === chat.id ? "active-chat" : ""}
                        onClick={() => onSelectChat(chat.id)}
                    >
                        {chat.title}
                    </li>
                ))}
            </ul>

            {/* 📌 Нижняя часть (лого + кнопка выхода) */}
            <div className="sidebar-footer">
                <button className="logout-btn" onClick={handleLogout}>Logout</button>
            </div>
        </div>
    );
}
