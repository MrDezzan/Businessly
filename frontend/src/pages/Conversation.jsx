import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { sanitize } from '../api/client';
import './Conversation.css';

export default function Conversation() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [conversation, setConversation] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchMessages, 5000); // Poll for new messages
        return () => clearInterval(interval);
    }, [id]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const fetchData = async () => {
        try {
            const [convRes, msgRes] = await Promise.all([
                api.get(`/api/conversations/${id}`),
                api.get(`/api/conversations/${id}/messages`),
            ]);
            setConversation(convRes.data);
            setMessages(msgRes.data.messages);
        } catch (error) {
            console.error('Failed to fetch conversation:', error);
            navigate('/dashboard');
        } finally {
            setLoading(false);
        }
    };

    const fetchMessages = async () => {
        try {
            const response = await api.get(`/api/conversations/${id}/messages`);
            setMessages(response.data.messages);
        } catch (error) {
            console.error('Failed to fetch messages:', error);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!newMessage.trim() || sending) return;

        setSending(true);
        try {
            await api.post(`/api/conversations/${id}/messages`, {
                content: sanitize(newMessage),
            });
            setNewMessage('');
            fetchMessages();
        } catch (error) {
            console.error('Failed to send message:', error);
        } finally {
            setSending(false);
        }
    };

    const toggleControl = async () => {
        if (!conversation) return;

        try {
            await api.put(`/api/conversations/${id}/control`, {
                is_ai_controlled: !conversation.is_ai_controlled,
            });
            setConversation({
                ...conversation,
                is_ai_controlled: !conversation.is_ai_controlled,
            });
        } catch (error) {
            console.error('Failed to toggle control:', error);
        }
    };

    if (loading) {
        return (
            <div className="page flex items-center justify-center">
                <div className="spinner" />
            </div>
        );
    }

    return (
        <div className="conversation-page">
            <div className="conversation-header">
                <button onClick={() => navigate('/dashboard')} className="btn btn-ghost btn-sm">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M19 12H5M12 19l-7-7 7-7" />
                    </svg>
                    Back
                </button>

                <div className="conversation-info">
                    <div className="conversation-avatar-lg">
                        {conversation?.telegram_first_name?.[0] || conversation?.telegram_username?.[0] || '?'}
                    </div>
                    <div>
                        <h2 className="conversation-name">
                            {conversation?.telegram_first_name || conversation?.telegram_username || 'Unknown'}
                        </h2>
                        {conversation?.telegram_username && (
                            <span className="conversation-username">@{conversation.telegram_username}</span>
                        )}
                    </div>
                </div>

                <div className="conversation-controls">
                    <span className={`badge ${conversation?.is_ai_controlled ? 'badge-success' : 'badge-warning'}`}>
                        {conversation?.is_ai_controlled ? 'AI Mode' : 'Manual Mode'}
                    </span>
                    <button onClick={toggleControl} className="btn btn-secondary btn-sm">
                        {conversation?.is_ai_controlled ? 'Take Control' : 'Enable AI'}
                    </button>
                </div>
            </div>

            <div className="messages-container">
                <div className="messages-list">
                    {messages.length === 0 ? (
                        <div className="no-messages">
                            <p>No messages yet</p>
                        </div>
                    ) : (
                        messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`message ${msg.role === 'user' ? 'message-user' : 'message-response'}`}
                            >
                                <div className="message-content">
                                    <p>{msg.content}</p>
                                </div>
                                <div className="message-meta">
                                    <span className="message-role">
                                        {msg.role === 'user' ? 'Customer' : msg.role === 'assistant' ? 'AI' : 'You'}
                                    </span>
                                    <span className="message-time">
                                        {new Date(msg.created_at).toLocaleTimeString('ru-RU', {
                                            hour: '2-digit',
                                            minute: '2-digit',
                                        })}
                                    </span>
                                </div>
                            </div>
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            <form onSubmit={handleSend} className="message-input-container">
                <input
                    type="text"
                    className="form-input message-input"
                    placeholder="Type your message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    disabled={sending}
                />
                <button type="submit" className="btn btn-primary" disabled={sending || !newMessage.trim()}>
                    {sending ? (
                        <span className="spinner" />
                    ) : (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="22" y1="2" x2="11" y2="13" />
                            <polygon points="22 2 15 22 11 13 2 9 22 2" />
                        </svg>
                    )}
                </button>
            </form>
        </div>
    );
}
