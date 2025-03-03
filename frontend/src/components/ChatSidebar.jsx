import { useNavigate } from "react-router-dom";

export default function ChatSidebar({ chats, selectedChat, onSelectChat, onNewChat, onDeleteChat }) {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/login");
    };

    return (
        <div className="chat-sidebar">
            <div className="sidebar-header">
                <img src="/logo.png" alt="Logo" className="logo" />
                <h1>ServiceGPT</h1>
            </div>
            <button className="new-chat-btn" onClick={onNewChat}>Новый чат</button>

            <h2>Чаты</h2>
            <ul>
                {chats.map((chat) => (
                    <li key={chat.id}
                        className={selectedChat === chat.id ? "active-chat" : ""}
                        onClick={() => onSelectChat(chat.id)}
                    >
                        {chat.title}
                        <span 
                          className="delete-chat"
                          onClick={(e) => {
                              e.stopPropagation();
                              onDeleteChat(chat.id);
                          }}
                        >
                          ✖
                        </span>
                    </li>
                ))}
            </ul>

            <div className="sidebar-footer">
                <button className="logout-btn" onClick={handleLogout}>Выход</button>
            </div>
        </div>
    );
}
